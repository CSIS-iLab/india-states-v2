import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { glob } from 'glob';

function getItems(dir, type) {
  if (!fs.existsSync(dir)) {
    console.warn(`⚠ Directory not found: ${dir}`);
    return [];
  }

  return glob.sync(`${dir}/**/*.md`).map(file => {
    const raw = fs.readFileSync(file, 'utf8');
    const { data } = matter(raw);
    const basename = path.basename(file, '.md');

    let id;
    if (type === 'posts') {
      const match = basename.match(/^(\d{4})-(\d{2})-(\d{2})-(.+)$/);
      id = match
        ? `/${match[1]}/${match[2]}/${match[3]}/${match[4]}`
        : `/${basename}`;
    } else {
      const match = basename.match(/^\d{4}-\d{2}-\d{2}-(.+)$/);
      id = match ? `/${match[1]}` : `/${basename}`;
    }

    return {
      id,
      title: data.title || basename,
      date: data.date ? new Date(data.date).toISOString() : '',
      tags: Array.isArray(data.tags)
        ? data.tags
        : data.tags
        ? [data.tags]
        : [],
    };
  });
}

function computeRelated(items) {
  const related = {};

  for (const item of items) {
    if (!item.tags.length) {
      related[toKey(item.id)] = [];
      continue;
    }

    const scores = [];
    for (const other of items) {
      if (other.id === item.id) continue;
      const shared = item.tags.filter(t => other.tags.includes(t)).length;
      if (shared > 0) {
        scores.push({ id: other.id, title: other.title, date: other.date, shared });
      }
    }

    related[toKey(item.id)] = scores
      .sort((a, b) => b.shared - a.shared)
      .slice(0, 4)
      .map(({ id, title, date }) => ({ id, title, date }));
  }

  return related;
}

function toKey(id) {
  return id.replace(/^\//, '').replace(/\//g, '__');
}

const posts = getItems('_posts', 'posts');
const newsletters = getItems('_newsletter', 'newsletter');

const output = {
  posts: computeRelated(posts),
  newsletter: computeRelated(newsletters),
};

fs.mkdirSync('_data', { recursive: true });
fs.writeFileSync('_data/related_posts.json', JSON.stringify(output));

console.log(`✓ Related posts: ${posts.length} articles, ${newsletters.length} newsletters`);
