const fs = require('fs');
const path = require('path');

const projectRoot = path.dirname(__dirname);
const schedulePath = path.join(projectRoot, 'schedule.json');
const indexPath = path.join(projectRoot, 'index.html');
const sitemapPath = path.join(projectRoot, 'sitemap.xml');

const schedule = JSON.parse(fs.readFileSync(schedulePath, 'utf8'));
let indexContent = fs.readFileSync(indexPath, 'utf8');
let sitemapContent = fs.readFileSync(sitemapPath, 'utf8');

function generateCardHtml(post) {
  return `        <!-- Post: ${post.filename} -->
        <article class="post-card">
          <div class="post-card-thumb" style="background-image: url('${post.image_url}');">
            <span class="post-tag">${post.tag}</span>
          </div>
          <div class="post-card-content">
            <div class="post-meta">
              <span>Author: Starrope</span>
              <span>•</span>
              <span>${post.date_display}</span>
            </div>
            <h3 class="post-card-title"><a href="posts/${post.filename}">${post.title}</a></h3>
            <p class="post-card-desc">${post.description}</p>
            <div class="post-card-footer">
              <a href="posts/${post.filename}" class="read-more-btn">
                Read Article
                <svg xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
          </div>
        </article>
`;
}

function isAlreadyPublished(filename, content) {
  const marker = '<!-- SCHEDULED_POSTS_START -->';
  const sidebarMarker = '<!-- RIGHT: SIDEBAR -->';
  if (!content.includes(marker)) return false;
  const startIdx = content.indexOf(marker);
  const endIdx = content.indexOf(sidebarMarker, startIdx);
  const gridContent = endIdx === -1 ? content.slice(startIdx) : content.slice(startIdx, endIdx);
  return gridContent.includes(`posts/${filename}`);
}

function insertCardToIndex(cardHtml, content) {
  const marker = '<!-- SCHEDULED_POSTS_START -->';
  if (!content.includes(marker)) {
    console.warn('Warning: Marker not found in index.html');
    return content;
  }
  return content.replace(marker, marker + '\n' + cardHtml);
}

function addUrlToSitemap(filename, publishDate, content) {
  if (content.includes(`posts/${filename}`)) return content;
  const newUrl = `  <url>
    <loc>https://blog2.starrope2023.com/posts/${filename}</loc>
    <lastmod>${publishDate}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
`;
  return content.replace('</urlset>', newUrl + '</urlset>');
}

const nowKst = new Date(new Date().getTime() + (9 * 60 * 60 * 1000));
const todayStr = nowKst.toISOString().split('T')[0];
console.log(`Current KST Date: ${todayStr}`);
let publishedCount = 0;

for (const post of schedule.posts) {
  if (isAlreadyPublished(post.filename, indexContent)) continue;
  if (post.publish_date <= todayStr) {
    console.log(`Publishing: ${post.filename} (${post.publish_date} ${post.publish_time})`);
    const cardHtml = generateCardHtml(post);
    indexContent = insertCardToIndex(cardHtml, indexContent);
    sitemapContent = addUrlToSitemap(post.filename, post.publish_date, sitemapContent);
    publishedCount++;
  }
}

if (publishedCount > 0) {
  fs.writeFileSync(indexPath, indexContent, 'utf8');
  console.log('index.html updated successfully.');
  fs.writeFileSync(sitemapPath, sitemapContent, 'utf8');
  console.log('sitemap.xml updated successfully.');
  console.log(`Successfully published ${publishedCount} posts!`);
} else {
  console.log('No posts to publish at this time.');
}
