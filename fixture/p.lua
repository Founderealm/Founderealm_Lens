local json = require("json")
local Omicron = {}
function Omicron.run(self) return 1 end
function helper() return Omicron.run(Omicron) + #tostring(json) end
