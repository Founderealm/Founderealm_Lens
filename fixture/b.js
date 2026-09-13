import fs from "fs";
const lodash = require("lodash");
class Beta { run() { return fs.readFileSync("x"); } }
function helper() { return new Beta().run(); }
