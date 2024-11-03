import markdown
from lxml import etree
from pprint import pprint
import typing
import yaml
import io
import os
from glob import glob
from datetime import date

type json_ty = None|bool|int|float|str|list[json_ty]|dict[str, json_ty]

NAVS = {
    'en': {
        'home': '/index.html',
        'about': '/en/about/about.html',
    },
    'zh': {
        'home': '/zh/index.html',
        'about': '/zh/about/关于.html',
    }
}

LANG_NAMES = {
    'zh' : '中文',
    'en' : 'English',
}

CONTACT = {
    'github': 'https://github.com/taimoon',
}

def get_parent_director(p: str) -> str:
    p, _ = os.path.split(p)
    return p

def default_copyright(name: str) -> str:
    from datetime import date
    return f'© {date.today().strftime('%Y')} {name}. All rights reserved.'

def makedir_p(p: str) -> None:
    if not os.path.exists(os.path.dirname(p)):
        os.makedirs(os.path.dirname(p))

def change_file_ext(path: str, ext: str) -> str:
    path, _ = os.path.splitext(path)
    return f'{path}.{ext}'

def get_file_stem(s: str) -> str:
    _, file_name = os.path.split(s)
    file_stem, _ = os.path.splitext(file_name)
    return file_stem

def sxml_to_html(e: typing.Any) -> etree.Element:
    match e:
        case str(tag),{**attrib},str(text):
            res = etree.Element(tag,attrib)
            res.text = text
            return res
        case str(tag),str(text):
            res = etree.Element(tag)
            res.text = text
            return res
        case str(tag),{**attrib},*es:
            res: etree._Element = etree.Element(tag,attrib)
            es = [sxml_to_html(e) for e in es]
            res.extend(es)
            return res
        case str(tag),*es:
            res: etree._Element = etree.Element(tag)
            es = [sxml_to_html(e) for e in es]
            res.extend(es)
            return res
        case _:
            raise NotImplementedError(e)

def meta_markdown_load(f: str|typing.TextIO) -> tuple[str, dict[str, json_ty]]:
    '''
    support only yaml frontmatter
    '''
    if isinstance(f, str):
        return meta_markdown_load(open(f, 'r'))
    affix = '---\n'
    ln = f.readline()
    if ln != affix:
        return ln + f.read(), None
    else:
        yml = ''
        ln = f.readline()
        while ln != affix:
            yml += ln
            ln = f.readline()
        content = f.read()
        # restrict yaml load only json
        yml = yaml.load(io.StringIO(yml), yaml.BaseLoader)
        return content, yml

def meta_markdown_loads(s: str) -> tuple[str, dict[str, json_ty]]:
    return meta_markdown_load(io.StringIO(s))

def markdown_to_html(path: str) -> tuple[str, dict[str, json_ty]]:
    content, md = meta_markdown_load(path)
    html = markdown.Markdown(extensions=['extra']).convert(content)
    return html, md

"""
def collect_tags(e: etree._Element|etree._ElementTree) -> set[str]:
    '''
    for development use
    '''
    def recur(e: etree._Element) -> set[str]:
        # getchildren will return empty list, thus terminate the function
        return reduce(set.union,
                      [recur(_e) for _e in e.getchildren()],{e.tag})
    if isinstance(e, etree._ElementTree):
        return recur(e.getroot())
    else:
        return recur(e)
"""

def convert_metadata(md: dict[str, json_ty]) -> dict[str, json_ty]:
    return {
     'date' : md.get('date',date.today().strftime('%Y-%m-%d')),
     'author': md['author'],
     'lang': md.get('lang','en'),
     'title': md['title'],
     'license': md.get('license',default_copyright(md['author'][0])),
     'category': md.get('category','uncategorized'),
    }

def fix_img_path(e: etree._Element, inp: str, out: str) -> None:
    src_dir, _ = os.path.split(inp)
    dest_dir, _ = os.path.split(out)
    html_dir = src_dir[src_dir.index('/') + 1:]
    
    for img in e.xpath('//img'):
        img: etree._Element
        img.attrib['src'] = os.path.join('/images',html_dir,img.attrib['src'])

def fix_extra_line_footnote(e: etree._Element):
    'WORKAROUND'
    for hr in e.xpath("//div[@class='footnote']/hr[1]"):
        hr: etree._Element
        hr.getparent().remove(hr)

def templatize(e: etree._Element, title: str, date: str, license: str, lang: str, others: dict[str, str]| None = None) -> None:
    if others is None:
        others = {}
    head = ['head',
            ['meta', {'date': date}],
            ['meta', {'charset': 'UTF-8'}],
            ['meta', {'name': 'viewport',
                      'content': 'width=device-width',
                      'initial-scale': '1.0'}],
            ['link', {'rel': 'stylesheet', 'href': '/style.css'}],
            ['title', title]]

    # add syntax highlighting
    if e.xpath('//code') != []:
        head.extend([
            ['link', {'rel': 'stylesheet', 'href': 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css'}],
            ['script', {'src': 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js'}, ''],
            ['script', 'hljs.highlightAll();'],
        ])

    # mathjax, with inline enable
    head.extend([
    ['script', {'id': 'MathJax-script', 'src': 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'}, ''],
    ['script',
    """
    MathJax.Hub.Config({
        tex2jax: {
        inlineMath: [ ['$','$'] ],
        processEscapes: true
        }
    });
    """],])
    header = ['header',
              ['nav',
               ['ul',
                *[['li',['a',{'href':lnk},txt]] for txt, lnk in NAVS[lang].items()],
                *[['li', ['a', {'href': lnk}, LANG_NAMES[lang]]] for lang, lnk in others.items()]]],]
    
    if license == 'CC BY-SA 4.0':
        footer = ['footer',
            ['a', {'href' : "https://creativecommons.org/licenses/by-sa/4.0/"}, f'COPYRIGHT NOTICE: {license}']
        ]
    else:
        footer = ['footer', 
            ['p', f'COPYRIGHT NOTICE: {license}']
        ]
    footer.extend(
        [['a', {'href': lnk}, txt] for txt, lnk in CONTACT.items()]
    )
    e.insert(0, sxml_to_html(head))
    e.insert(1, sxml_to_html(header))
    e.append(sxml_to_html(footer))
    if date != '':
        _e: etree._Element = e.xpath('//main')[0]
        _e.insert(0, sxml_to_html(['p', f'date: {date}']))

def build_page(html_str: str, metadata:dict[str, list[str]], out: str, inp: str, others: dict[str, str]) -> None:
    makedir_p(out)
    title = metadata['title']
    date = metadata['date']
    lang: str =  metadata['lang']
    license = metadata['license']

    html_ast: etree._Element = etree.fromstring(
        f'<html lang="{lang}"><main>{html_str}</main></html>'
        )

    templatize(html_ast, title, date, license, lang, others)

    # WORKAROUND
    fix_img_path(html_ast, inp, out)
    fix_extra_line_footnote(html_ast)

    s: bytes = etree.tostring(html_ast,encoding = 'utf-8', pretty_print = True)

    with open(out,'wb+') as f:
        f.write(s)  

def create_home(metadatas: list[dict[str, json_ty]], out: str, lang: str) -> None:
    metadatas = [v for v in metadatas if v['metadata'].get('category',None) != 'about']
    create_entry = lambda txt, lnk : ['li', ['a', {'href': lnk}, txt]]

    index = {
        w['metadata']['category']:
        [[v['title'], v['url']] for v in metadatas
         if v['metadata']['category'] == w['metadata']['category']]
        for w in metadatas
    }

    index = [['ul', ['h1',cat], *[create_entry(txt, lnk) for txt, lnk in corspd]] for cat, corspd in index.items()]
    e = ['html', ['body', ['nav', *index]]]
    e = sxml_to_html(e)
    templatize(e, 'index', '', 'CC BY-SA 4.0', lang, {l: navs['home'] for l, navs in NAVS.items() if l != lang})
    b: bytes = etree.tostring(e, encoding = 'utf-8', pretty_print = True)
    makedir_p(out)

    with(open(out, 'wb+')) as f:
        f.write(b)

def build_site(root: str):
    makedir_p(f'{root}/')
    os.system(f"cp style.css {root}/")

    inps = glob('content/**/*.md', recursive=True)
    urls = [change_file_ext(inp.removeprefix('content/'), 'html') for inp in inps]
    pages = [markdown_to_html(inp) for inp in inps]
    pages = [(s, convert_metadata(md)) for s, md in pages]
    kwargss = [{
            'title': get_file_stem(inp),
            'html_str': html_str,
            'url': os.path.join('/',metadata['lang'], url),
            'inp': inp,
            'out': os.path.join('site',metadata['lang'], url),
            'metadata': metadata,
        } for (html_str, metadata), url, inp in zip(pages, urls, inps)]

    # collect languages
    draft = {get_parent_director(d['inp']): [] for d in kwargss}
    for d in kwargss:
        draft[get_parent_director(d['inp'])].append(d)
    draft = {f:{md['metadata']['lang']:md['url'] for md in mds} for f, mds in draft.items()}
    
    kwargss = [
        {**kwargs, 
         "others": {lang: url for lang, url in draft[get_parent_director(kwargs['inp'])].items() 
                    if kwargs['metadata']['lang'] != lang},}
        for kwargs in kwargss]
    imgs = [(src, os.path.join('site/images', src.removeprefix('content/'))) for src in glob('content/**/*.png', recursive=True)]
    for src, dest in imgs:
        makedir_p(dest)
        os.system(f'cp "{src}" "{dest}"')

    for kwargs in kwargss:
        build_page(kwargs['html_str'], kwargs['metadata'], kwargs['out'], kwargs['inp'], kwargs['others'])

    metadatas = kwargss
    zh_metadatas = [v for v in metadatas if v['metadata']['lang'] == 'zh']
    create_home(zh_metadatas, 'site/zh/index.html', 'zh')
    en_metadatas = [v for v in metadatas if v['metadata']['lang'] == 'en']
    create_home(en_metadatas, 'site/index.html', 'en')

if __name__ == '__main__':
    build_site('site')