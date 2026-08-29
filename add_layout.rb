require 'fileutils'

ARCHIVE_DIRS = ['_newsletter_archive', '_posts_archive']

ARCHIVE_DIRS.each do |dir|
  unless Dir.exist?(dir)
    puts "Skipping #{dir} — directory not found"
    next
  end

  files = Dir.glob("#{dir}/**/*.md")
  puts "Processing #{files.count} files in #{dir}..."

  files.each do |file|
    content = File.read(file)

    # Skip if layout is already defined
    if content.match?(/^layout:/)
      puts "  [SKIP] #{file} — layout already set"
      next
    end

    # Inject layout: post right after the opening ---
    updated = content.sub(/\A---\n/, "---\nlayout: post\n")

    File.write(file, updated)
    puts "  [DONE] #{file}"
  end
end

puts "\nAll done!"
