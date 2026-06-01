#!/usr/bin/env python3
"""
Starrope Tech & AI Blog - Auto Scheduled Post Publisher
Runs on GitHub Actions at 8:00 AM and 4:00 PM KST
"""

import json
import os
from datetime import datetime, timezone, timedelta

# KST = UTC+9
KST = timezone(timedelta(hours=9))

def get_current_kst():
    return datetime.now(timezone.utc).astimezone(KST)

def generate_card_html(post):
    return f"""        <!-- Post: {post['filename']} -->
        <article class="post-card">
          <div class="post-card-thumb" style="background-image: url('{post['image_url']}');">
            <span class="post-tag">{post['tag']}</span>
          </div>
          <div class="post-card-content">
            <div class="post-meta">
              <span>Author: Starrope</span>
              <span>&bull;</span>
              <span>{post['date_display']}</span>
            </div>
            <h3 class="post-card-title"><a href="posts/{post['filename']}">{post['title']}</a></h3>
            <p class="post-card-desc">{post['description']}</p>
            <div class="post-card-footer">
              <a href="posts/{post['filename']}" class="read-more-btn">
                Read Article
                <svg xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
          </div>
        </article>
"""

def is_already_published(filename, index_content):
    return f'posts/{filename}' in index_content

def insert_card_to_index(card_html, index_content):
    marker = '<!-- SCHEDULED_POSTS_START -->'
    if marker not in index_content:
        print("Warning: marker not found.")
        return index_content
    return index_content.replace(marker, marker + '\n' + card_html, 1)

def add_url_to_sitemap(filename, publish_date, sitemap_content):
    if f'posts/{filename}' in sitemap_content:
        return sitemap_content
    new_url = f"""  <url>
    <loc>https://blog2.starrope2023.com/posts/{filename}</loc>
    <lastmod>{publish_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
"""
    return sitemap_content.replace('</urlset>', new_url + '</urlset>')

def main():
    now = get_current_kst()
    today = now.date()
    current_hour = now.hour
    print(f"Current KST Time: {now.strftime('%Y-%m-%d %H:%M')}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    with open(os.path.join(project_root, 'schedule.json'), 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    index_path = os.path.join(project_root, 'index.html')
    sitemap_path = os.path.join(project_root, 'sitemap.xml')

    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
    with open(sitemap_path, 'r', encoding='utf-8') as f:
        sitemap_content = f.read()

    published_count = 0

    for post in schedule['posts']:
        post_date_str = post['publish_date']
        post_time = post['publish_time']
        post_date = datetime.strptime(post_date_str, '%Y-%m-%d').date()

        if is_already_published(post['filename'], index_content):
            continue

        should_publish = False
        if post_date < today:
            should_publish = True
        elif post_date == today:
            post_hour = int(post_time.split(':')[0])
            if current_hour >= post_hour:
                should_publish = True

        if should_publish:
            filename = post['filename']
            print(f"Publishing: {filename} ({post_date_str} {post_time})")
            card_html = generate_card_html(post)
            index_content = insert_card_to_index(card_html, index_content)
            sitemap_content = add_url_to_sitemap(filename, post_date_str, sitemap_content)
            published_count += 1

    if published_count > 0:
        print(f"\nPublished {published_count} posts!")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        print("Done.")
    else:
        print("No posts to publish.")

if __name__ == '__main__':
    main()
