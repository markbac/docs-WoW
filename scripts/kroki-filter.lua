-- kroki-filter.lua
--
-- Unified diagram rendering via Kroki
-- - Supports multiple diagram types
-- - Outputs PDF for LaTeX, SVG for EPUB
-- - Caching via content hash
-- - Retry via curl
-- - Graceful failure with visible fallback
-- - Debug logging for CI (GitHub Actions compatible)

local path = require("pandoc.path")

local output_dir = "_diagrams"
local log_file = path.join({output_dir, "kroki-errors.log"})
local kroki_url = os.getenv("KROKI_URL") or "https://kroki.io"

os.execute("mkdir -p " .. output_dir)

-- =================================================
-- Debug / logging
-- =================================================

local DEBUG = os.getenv("KROKI_DEBUG") == "1"

local function dbg(msg)
  if DEBUG then
    io.stderr:write("[kroki] " .. msg .. "\n")
  end
end

local function gha_warn(msg)
  io.stderr:write("::warning::" .. msg .. "\n")
end

local function gha_error(msg)
  io.stderr:write("::error::" .. msg .. "\n")
end

local function log_error(msg)
  local f = io.open(log_file, "a")
  f:write(os.date("%Y-%m-%d %H:%M:%S") .. " | " .. msg .. "\n")
  f:close()
end

-- =================================================
-- Helpers
-- =================================================

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

-- =================================================
-- Language handling
-- =================================================

local aliases = {
  uml = "plantuml",
  puml = "plantuml",
  c4 = "c4plantuml",
  graphviz = "dot",
  gv = "dot"
}

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
  wireviz = true -- may require self-hosted Kroki
}

-- =================================================
-- Main handler
-- =================================================

function CodeBlock(el)
  local lang = el.classes[1]
  if not lang then return nil end

  if aliases[lang] then
    lang = aliases[lang]
  end

  if not supported[lang] then
    return nil
  end

  dbg("Processing block lang=" .. lang)

  local h = hash(el.text)

  -- format selection
  local format = FORMAT:match("latex") and "pdf" or "svg"

  local outfile = path.join({output_dir, h .. "." .. format})
  local infile = path.join({output_dir, h .. ".txt"})

  -- =================================================
  -- Cache check
  -- =================================================

  local f = io.open(outfile, "r")
  if f then
    f:close()
    dbg("Cache hit: " .. outfile)
    return pandoc.Para({
      pandoc.Image({}, outfile, "", { width = "95%" })
    })
  end

  -- =================================================
  -- Render via Kroki
  -- =================================================

  write_file(infile, el.text)

  local url = string.format("%s/%s/%s", kroki_url, lang, format)

  dbg("Rendering via Kroki: " .. lang)
  dbg("Input: " .. infile)
  dbg("Output: " .. outfile)
  dbg("URL: " .. url)

  local cmd = string.format(
    "curl -s -f --retry 3 --retry-delay 1 --retry-all-errors " ..
    "-X POST --data-binary @%s %s -o %s",
    infile,
    url,
    outfile
  )

  dbg("Executing: " .. cmd)
  local ok = os.execute(cmd)
  dbg("Exit code: " .. tostring(ok))

  -- =================================================
  -- Failure handling
  -- =================================================

  if ok ~= 0 then
    local msg = string.format("FAILED [%s] hash=%s", lang, h)

    log_error(msg)
    dbg(msg)
    gha_error(msg)

    return {
      pandoc.Para({
        pandoc.Str("[Diagram failed to render: " .. lang .. "]")
      }),
      el
    }
  end

  dbg("Rendered successfully: " .. outfile)

  -- =================================================
  -- Success
  -- =================================================

  return pandoc.Para({
    pandoc.Image({}, outfile, "", {
      width = "95%"
    })
  })
end