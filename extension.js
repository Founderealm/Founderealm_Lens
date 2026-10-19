// Founderealm Lens in VS Code: the release the Claude Code plugin runs, started by VS Code.
//
// server/RELEASE names the release and server/SHA256SUMS the SHA-256 of each of its
// binaries. The binary for this machine is downloaded once into the extension's storage and
// run only if its SHA-256 matches the one in SHA256SUMS: the expected hash comes from the
// extension as installed, not from the place the binary is downloaded from. A local build in
// server/ wins, for development, as it does for the plugin's launcher.
'use strict';
const vscode = require('vscode');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const issues = 'open an issue at https://github.com/Founderealm/Founderealm_Lens/issues.';
const sha = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');

function activate(context) {
    const here = path.join(context.extensionPath, 'server');
    const os = { darwin: 'darwin', linux: 'linux', win32: 'windows' }[process.platform];
    const arch = { arm64: 'arm64', x64: 'x86_64' }[process.arch];
    const exe = os === 'windows' ? '.exe' : '';
    const name = `founderealm-lens-${os}-${arch}${exe}`;
    const release = fs.readFileSync(path.join(here, 'RELEASE'), 'utf8').trim();
    const want = fs.readFileSync(path.join(here, 'SHA256SUMS'), 'utf8').split('\n')
        .map((line) => line.trim().split(/\s+/))
        .find(([, file]) => file && file.replace(/^\*/, '') === name)?.[0];
    const local = path.join(here, `founderealm-lens${exe}`);
    const store = context.globalStorageUri.fsPath;
    const bin = fs.existsSync(local) ? local : path.join(store, release, name);

    // Why this machine cannot run the release, if it cannot.
    const unsupported = !os ? `no prebuilt binary for ${process.platform}; ${issues}`
        // Apple silicon only: no current macOS runs on an Intel Mac.
        : os === 'darwin' && arch === 'x86_64' ? `no prebuilt binary for Intel Macs; ${issues}`
        : !arch ? `no prebuilt binary for ${process.arch}; ${issues}`
        : !want ? `release ${release} has no binary for ${os}-${arch}.`
        : null;

    async function fetchOnce() {
        if (fs.existsSync(bin) && sha(fs.readFileSync(bin)) === want) return;
        const url = `https://github.com/Founderealm/Founderealm_Lens/releases/download/${release}/${name}`;
        const body = await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Founderealm Lens: fetching ${name} from release ${release}`,
        }, async () => {
            const res = await fetch(url).catch((e) => ({ ok: false, status: e.cause?.message ?? e.message }));
            if (!res.ok) throw new Error(`could not download ${url}: ${res.status}`);
            return Buffer.from(await res.arrayBuffer());
        });
        const got = sha(body);
        if (got !== want) throw new Error(`SHA-256 of ${name} is ${got}, expected ${want}. It was not kept, and nothing was run.`);
        fs.mkdirSync(path.dirname(bin), { recursive: true });
        const part = `${bin}.part.${process.pid}`;
        fs.writeFileSync(part, body, { mode: 0o755 });
        fs.renameSync(part, bin);
        // Only the release in use is kept. A binary still running from an older one stays
        // where Windows will not delete it, until the next fetch.
        for (const old of fs.readdirSync(store)) {
            if (old !== release) try { fs.rmSync(path.join(store, old), { recursive: true, force: true }); } catch {}
        }
    }

    context.subscriptions.push(vscode.lm.registerMcpServerDefinitionProvider('founderealm-lens', {
        provideMcpServerDefinitions: () => [
            new vscode.McpStdioServerDefinition('Founderealm Lens', bin, ['mcp'], {}, release),
        ],
        resolveMcpServerDefinition: async (server) => {
            if (bin !== local) {
                if (unsupported) throw new Error(unsupported);
                await fetchOnce();
            }
            return server;
        },
    }));
}

module.exports = { activate };
