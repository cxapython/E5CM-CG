# Repository Notes

- In this repository, before running PowerShell commands that print file contents or search results, set console output encoding to UTF-8 first:
  `$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()`
- Prefer `Get-Content -Encoding UTF8` when reading source files that may contain Chinese text.
- After analyzing or comparing local video files, delete any temporary artifacts you created before finishing unless the user explicitly asks to keep them. This includes extracted frames, ffmpeg outputs, scratch images, and `_tmp*` files or directories.
- Layout scaling rule: all UI layouts in this repository should use proportional scaling by default. If a layout is authored relative to a background, panel, or parent container, then child rects, font sizes, stroke widths, letter spacing, and content offsets must follow that parent container's actual runtime scale. Do not scale child elements only by the full-screen resolution when the parent container has its own capped size or different runtime scale. Only use non-uniform stretching when the design explicitly requires it.
