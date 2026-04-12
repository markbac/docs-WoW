-- chapter_mapping.lua
-- Goal:
--   #  ... = structural "sections" (front matter + parts)
--   ## ... = numbered chapters
--
-- Rules:
--   - Preface/Acknowledgements => \chapter* (front matter style) + TOC entry
--   - Introduction             => \chapter* + TOC entry (doesn't steal Chapter 1)
--   - Other # headings          => \part
--   - ## headings               => \chapter

local stringify = pandoc.utils.stringify

local function latex_frontmatter_section(title)
  return {
    pandoc.RawBlock("latex", "\\clearpage"),
    pandoc.RawBlock("latex", "\\phantomsection"),
    pandoc.RawBlock("latex", "\\section*{" .. title .. "}"),
    pandoc.RawBlock("latex", "\\addcontentsline{toc}{section}{" .. title .. "}"),
  }
end


local function latex_part(title)
  return {
    pandoc.RawBlock("latex", "\\clearpage"),
    pandoc.RawBlock("latex", "\\section*{" .. title .. "}"),
    pandoc.RawBlock("latex", "\\addcontentsline{toc}{section}{" .. title .. "}"),
  }
end

function Header(el)
  local title = stringify(el.content)

  if FORMAT:match("latex") then
    if el.level == 1 then
      local t = title:lower()

        if t == "preface" or t == "acknowledgements" or t == "acknowledgments" then
        return latex_frontmatter_section(title)
        end


        if t == "introduction" then
        return latex_frontmatter_section(title)
        end


      -- Your “Section I …” etc
      return latex_part(title)
    end

    if el.level == 2 then
      -- Promote ## to a real chapter
      return pandoc.Header(1, el.content, el.attr)
    end
  end

  return el
end
