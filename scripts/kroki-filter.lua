-- kroki-filter.lua
--
-- Robust Kroki rendering filter with:
-- - correct success detection
-- - full request/response debug logging
-- - GitHub Actions visibility
-- - graceful fallback

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

local function file_exists(name)
  local f = io.open(name, "r")
  if f then f:close() return true end
  return false
end

local function read_file_head(filename, max_bytes)
  local f = io.open(filename, "r")
  if not f then return "" end
  local content = f:read(max_bytes or 500)
  f:close()
  return content or ""
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
  wireviz = true
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
  local format = "png"

  local outfile = path.join({output_dir, h .. "." .. format})
  local infile = path.join({output_dir, h .. ".txt"})
  local headers_file = path.join({output_dir, h .. ".headers"})

  -- =================================================
  -- Cache check
  -- =================================================

  if file_exists(outfile) then
    dbg("Cache hit: " .. outfile)
    return pandoc.Para({
      pandoc.Image({}, outfile)
    })
  end

  write_file(infile, el.text)

  local url = string.format("%s/%s/%s", kroki_url, lang, format)

  dbg("--------------------------------------------------")
  dbg("KROKI REQUEST")
  dbg("URL: " .. url)
  dbg("INPUT FILE: " .. infile)
  dbg("OUTPUT FILE: " .. outfile)
  dbg("FORMAT: " .. format)
  dbg("--------------------------------------------------")

  local cmd = string.format(
    "curl -s -f --retry 3 --retry-delay 1 --retry-all-errors " ..
    "-D %s " ..                -- capture headers
    "-X POST --data-binary @%s %s -o %s",
    headers_file,
    infile,
    url,
    outfile
  )

  dbg("Executing: " .. cmd)

  local ok, _, code = os.execute(cmd)

  dbg("os.execute raw result: " .. tostring(ok))
  dbg("exit code: " .. tostring(code))

  -- =================================================
  -- Validate success via file existence
  -- =================================================

  local success = file_exists(outfile)

  if success then
    dbg("KROKI RESPONSE (headers):")
    dbg(read_file_head(headers_file, 1000))

    dbg("Output file size OK: " .. outfile)
    dbg("--------------------------------------------------")

    return pandoc.Para({
      pandoc.Image({}, outfile, "", { width = "95%" })
    })
  end

  -- =================================================
  -- Failure handling with full diagnostics
  -- =================================================

  local response_preview = read_file_head(headers_file, 1000)

  local msg = string.format(
    "FAILED [%s] hash=%s\nHeaders:\n%s",
    lang,
    h,
    response_preview
  )

  log_error(msg)
  dbg(msg)
  gha_error("Kroki render failed for " .. lang)

  return {
    pandoc.Para({
      pandoc.Str("[Diagram failed to render: " .. lang .. "]")
    }),
    el
  }
end