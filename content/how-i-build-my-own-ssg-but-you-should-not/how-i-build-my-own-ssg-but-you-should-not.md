---
title: How I Build My Own Static Site Generator But You Should Not
author: Leong Teng Man
date: 2024-11-05
tags:
    - webdev
    - blogging
category: misc
license: CC BY-SA 4.0
lang: en
---
# How I Build My Own Static Site Generator But You Should Not

The title is indeed a clickbait.

TL;DR: Don't build your own SSG and use framework instead if you doesn't have particular needs.

# Why I build my SSG?

Before building my own SSG, I've almost zero knowledge about web development that's why I built it for learning purpose.

# How I build my SSG?

Depends on your requirements, sometimes, you don't need SSG.
For instance, if you're about to blog like [danluu.com](https://danluu.com/), 
then it is sufficient to handwritten your content in pure html.

On high level, my SSG does these thing

1. Collect inputs and copy pictures
2. Convert input markdowns to YAML (metadata) and HTML (content)
3. Apply template to the HTML
4. Generate sitemap
5. Generate RSS feed
6. Commit and push to github pages for publish

I use `python` to implement my SSG, the components are:

1. markdown parser (`Markdown`)
2. YAML parser (`pyyaml`)
3. HTML processor (`lxml`)
4. linter (highlightjs.org)
5. math renderer (mathjax.org)
6. template engine
7. http server (for local preview)

# Things I miss
Python Markdown library its extension `meta` does not parse markdown frontmatter as if YAML rather it has its own.
Due to that, I've to implement a function that will parse frontmatter only then using python Markdown to parse the remaining content.
In addition, the library itself does not have extension to process math display enclosed by `$` and `$$` into special HTML elements.
The lesson here is to use a better library.

Sometimes, it's a bliss to do monolingual site. When the content is in multilingual, it complicates the things such as

- how visitors pick a language and navigate your websites
- how content is presented for each language, for example in blog, how category pages should presented? should they share the same page? or having one for each language?
- generate sitemap

I would recommend using template engine like jinja2.
For my case, I wrote a pass to apply template, but the template is hard baked into the function `templatize`. Probably, it is not really worth to do that for the sake of reducing template engine dependecy. I wrote a constructor that accept `SXML` and return `lxml`'s elements. I use this to implement the `templatize` and RSS feed.

# Suggested
- [https://blog.pesky.moe/posts/2023-11-04-custom-ssg/](https://blog.pesky.moe/posts/2023-11-04-custom-ssg/)
- [https://arne.me/blog/write-your-own-ssg](https://arne.me/blog/write-your-own-ssg)
- [https://www.gnu.org/software/guile/manual/html_node/SXML.html](https://www.gnu.org/software/guile/manual/html_node/SXML.html)
- [https://danluu.com/web-bloat/](https://danluu.com/web-bloat/)