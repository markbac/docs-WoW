-- kroki-filter.lua
--
-- Fail-safe diagram rendering via Kroki
-- - retries
-- - logs failures
-- - graceful fallback in output

local path = require("pandoc.path")

local output_dir = "_diagrams"
local log_file = path.join({output_dir, "kroki-errors.log"})
local kroki_url = os.getenv("KROKI_URL") or "https://kroki.io"

os.execute("mkdir -p " .. output_dir)

-- simple hash
local function hash(str)
  local h = 0
  for i = 1, #str do
    h = (h * 33 + str:byte(i)) % 2^32
  end
  return string.format("%x", h)
end

local function write_file(filename, content)
  local f = io.open(filename, "w")
  f:write(content)
  f:close()
end

local function log_error(msg)
  local f = io.open(log_file, "a")
  f:write(os.date("%Y-%m-%d %H:%M:%S") .. " | " .. msg .. "\n")
  f:close()
end

-- aliases
local aliases = {
  uml = "plantuml",
  puml = "plantuml",
  c4 = "c4plantuml",
  graphviz = "dot",
  gv = "dot"
}

-- supported
local supported = {
  mermaid = true,
  plantuml = true,
  c4plantuml = true,
  structurizr = true,
  dot = true,
  vega = true,
  vegalite = true,
  wavedrom = true,
  bytefield = true,
  seqdiag = true,
  actdiag = true,
  blockdiag = true,
  nwdiag = true,
  packetdiag = true,
  rackdiag = true,
  d2 = true,
  nomnoml = true,
  wireviz = true
}

function CodeBlock(el)
  local lang = el.classes[1]
  if not lang then return nil end

  if aliases[lang] then
    lang = aliases[lang]
  end

  if not supported[lang] then
    return nil
  end

  local h = hash(el.text)
  local outfile = path.join({output_dir, h .. ".svg"})
  local infile = path.join({output_dir, h .. ".txt"})

  -- cache check
  local f = io.open(outfile, "r")
  if f then
    f:close()
    return pandoc.Para({ pandoc.Image({}, outfile) })
  end

  write_file(infile, el.text)

  local url = string.format("%s/%s/svg", kroki_url, lang)

  local cmd = string.format(
    "curl -s -f --retry 3 --retry-delay 1 --retry-all-errors " ..
    "-X POST --data-binary @%s %s -o %s",
    infile,
    url,
    outfile
  )

  local ok = os.execute(cmd)

  if ok ~= 0 then
    local msg = string.format("FAILED [%s] hash=%s", lang, h)
    log_error(msg)

    -- visible fallback in document
    return {
      pandoc.Para({
        pandoc.Str("[Diagram failed to render: " .. lang .. "]")
      }),
      el -- include original code block for reference
    }
  end

  return pandoc.Para({
    pandoc.Image({}, outfile, "", {
        width = "95%",
        height = "90vh"
        })
  })
end