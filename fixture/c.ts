import { readFile } from "fs";
interface Shape { area(): number }
type Id = string;
class Gamma implements Shape { area(): number { return readFile.length; } }
function helper(): Id { return new Gamma().area().toString(); }
