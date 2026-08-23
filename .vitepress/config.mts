import {defineConfig} from 'vitepress'
import {existsSync} from 'node:fs'
import {resolve} from 'node:path'
import {fileURLToPath} from 'node:url'

const siteUrl = 'https://docs.termark.app'
const contentRoot = fileURLToPath(new URL('..', import.meta.url))

function routeFor(relativePath: string) {
    const withoutExtension = relativePath.replace(/\.md$/, '')
    if (withoutExtension === 'index') return '/'
    if (withoutExtension.endsWith('/index')) return `/${withoutExtension.slice(0, -6)}/`
    return `/${withoutExtension}`
}

function alternateRoutes(relativePath: string) {
    const route = routeFor(relativePath)
    const englishRoute = route.startsWith('/zh/') ? route.slice(3) || '/' : route
    const chineseRoute = route.startsWith('/zh/') ? route : `/zh${route}`
    const counterpart = relativePath.startsWith('zh/')
        ? relativePath.slice(3)
        : `zh/${relativePath}`
    return {route, englishRoute, chineseRoute, hasTranslation: existsSync(resolve(contentRoot, counterpart))}
}

function isoDate(value: unknown) {
    if (value instanceof Date) return value.toISOString().slice(0, 10)
    if (typeof value === 'string') return value.slice(0, 10)
    return undefined
}

const logo = {
    src: '/logo.svg',
    alt: 'Termark'
}

const copyright = 'Copyright © 2026 Termark'

export default defineConfig({
    cleanUrls: true,
    sitemap: {
        hostname: siteUrl,
        xmlns: {
            news: false,
            video: false,
            xhtml: false,
            image: false
        },
        transformItems(items) {
            return items.map(({links, ...item}) => ({
                ...item,
                url: item.url.replace(/\.html$/, '')
            }))
        }
    },
    transformHead({pageData}) {
        const {route, englishRoute, chineseRoute, hasTranslation} = alternateRoutes(pageData.relativePath)
        const languageLinks = hasTranslation ? [
            ['link', {rel: 'canonical', href: `${siteUrl}${route}`}],
            ['link', {rel: 'alternate', hreflang: 'en', href: `${siteUrl}${englishRoute}`}],
            ['link', {rel: 'alternate', hreflang: 'zh-CN', href: `${siteUrl}${chineseRoute}`}],
            ['link', {rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}${englishRoute}`}]
        ] : [
            ['link', {rel: 'canonical', href: `${siteUrl}${route}`}]
        ]
        const head = [
            ...languageLinks,
            ['meta', {property: 'og:url', content: `${siteUrl}${route}`}],
            ['meta', {property: 'og:site_name', content: 'Termark'}],
            ['meta', {name: 'robots', content: 'index, follow, max-image-preview:large'}]
        ]
        if (route.startsWith('/blog/') && route !== '/blog/') {
            const title = pageData.frontmatter.title || pageData.title
            const description = pageData.frontmatter.description || ''
            const published = isoDate(pageData.frontmatter.date)
            const modified = isoDate(pageData.frontmatter.updated) || published
            const author = pageData.frontmatter.author || 'Termark Team'
            const image = pageData.frontmatter.image
            const article = {
                '@context': 'https://schema.org', '@type': 'BlogPosting', headline: title, description,
                ...(published ? {datePublished: published} : {}), ...(modified ? {dateModified: modified} : {}),
                author: {'@type': 'Organization', name: author, url: 'https://www.termark.app/'},
                publisher: {'@type': 'Organization', '@id': 'https://www.termark.app/#organization', name: 'Termark', url: 'https://www.termark.app/', sameAs: ['https://github.com/termark-app/termark', 'https://t.me/termark_app'], logo: {'@type': 'ImageObject', url: 'https://www.termark.app/logo.svg'}},
                mainEntityOfPage: {'@type': 'WebPage', '@id': `${siteUrl}${route}`},
                ...(image ? {image: image.startsWith('http') ? image : `${siteUrl}${image}`} : {})
            }
            const breadcrumbs = {
                '@context': 'https://schema.org', '@type': 'BreadcrumbList',
                itemListElement: [
                    {'@type': 'ListItem', position: 1, name: 'Termark Documentation', item: `${siteUrl}/`},
                    {'@type': 'ListItem', position: 2, name: 'Blog', item: `${siteUrl}/blog/`},
                    {'@type': 'ListItem', position: 3, name: title, item: `${siteUrl}${route}`}
                ]
            }
            if (published) head.push(['meta', {property: 'article:published_time', content: published}])
            if (modified) head.push(['meta', {property: 'article:modified_time', content: modified}])
            head.push(
                ['script', {type: 'application/ld+json'}, JSON.stringify(article)],
                ['script', {type: 'application/ld+json'}, JSON.stringify(breadcrumbs)]
            )
        }
        if (route.startsWith('/zh/blog/') && route !== '/zh/blog/') {
            const title = pageData.frontmatter.title || pageData.title
            const description = pageData.frontmatter.description || ''
            const published = isoDate(pageData.frontmatter.date)
            const modified = isoDate(pageData.frontmatter.updated) || published
            const author = pageData.frontmatter.author || 'Termark Team'
            const image = pageData.frontmatter.image
            const article = {
                '@context': 'https://schema.org', '@type': 'BlogPosting', headline: title, description,
                ...(published ? {datePublished: published} : {}), ...(modified ? {dateModified: modified} : {}),
                author: {'@type': 'Organization', name: author, url: 'https://www.termark.app/zh-cn/'},
                publisher: {'@type': 'Organization', '@id': 'https://www.termark.app/#organization', name: 'Termark', url: 'https://www.termark.app/', sameAs: ['https://github.com/termark-app/termark', 'https://t.me/termark_app'], logo: {'@type': 'ImageObject', url: 'https://www.termark.app/logo.svg'}},
                mainEntityOfPage: {'@type': 'WebPage', '@id': `${siteUrl}${route}`},
                ...(image ? {image: image.startsWith('http') ? image : `${siteUrl}${image}`} : {})
            }
            const breadcrumbs = {
                '@context': 'https://schema.org', '@type': 'BreadcrumbList',
                itemListElement: [
                    {'@type': 'ListItem', position: 1, name: 'Termark 文档', item: `${siteUrl}/zh/`},
                    {'@type': 'ListItem', position: 2, name: '中文博客', item: `${siteUrl}/zh/blog/`},
                    {'@type': 'ListItem', position: 3, name: title, item: `${siteUrl}${route}`}
                ]
            }
            if (published) head.push(['meta', {property: 'article:published_time', content: published}])
            if (modified) head.push(['meta', {property: 'article:modified_time', content: modified}])
            head.push(
                ['script', {type: 'application/ld+json'}, JSON.stringify(article)],
                ['script', {type: 'application/ld+json'}, JSON.stringify(breadcrumbs)]
            )
        }
        return head
    },
    lang: 'en-US',
    title: 'Termark',
    description: 'Termark documentation',
    head: [
        ['link', {rel: 'icon', type: 'image/svg+xml', href: '/logo.svg'}],
        ['script', {
            defer: '',
            src: 'https://umami.next-terminal.com/script.js',
            'data-website-id': 'dd1a2266-3b28-4646-b8b4-107f0fb640dd',
            'data-domains': 'docs.termark.app'
        }]
    ],
    locales: {
        root: {
            label: 'English',
            lang: 'en-US',
            link: '/',
            description: 'Termark Documentation',
            themeConfig: {
                logo,
                nav: [
                    {text: 'Docs', link: '/usage/sftp-cwd-tracking'},
                    {
                        text: 'Changelog',
                        items: [
                            {text: 'Desktop Changelog', link: '/changelog'},
                            {text: 'Mobile Changelog', link: '/mobile-changelog'}
                        ]
                    },
                    {text: 'Blog', link: '/blog/termark-ssh-terminal-workbench'},
                    {text: 'Official Website', link: 'https://www.termark.app/'}
                ],
                sidebar: {
                    '/usage/': [
                        {
                            text: 'Documentation',
                            items: [
                                {text: 'SFTP CWD Tracking', link: '/usage/sftp-cwd-tracking'},
                                {text: 'Keyword Highlight', link: '/usage/terminal-keyword-highlight'},
                                {text: 'PowerShell Light Mode Display Issues', link: '/usage/powershell-light-theme'},
                                {text: 'Windows Antivirus False Positive Notice', link: '/usage/windows-virus-warning'},
                                {text: 'Local Encryption and Data Recovery', link: '/usage/local-encryption'},
                                {text: 'Data Storage Path', link: '/usage/data-storage-path'},
                            ]
                        }
                    ],
                    '/changelog': [
                        {
                            text: 'Release Notes',
                            items: [
                                {text: 'Desktop Changelog', link: '/changelog'},
                                {text: 'Mobile Changelog', link: '/mobile-changelog'}
                            ]
                        }
                    ],
                    '/mobile-changelog': [
                        {
                            text: 'Release Notes',
                            items: [
                                {text: 'Desktop Changelog', link: '/changelog'},
                                {text: 'Mobile Changelog', link: '/mobile-changelog'}
                            ]
                        }
                    ],
                    '/blog/': [
                        {
                            text: 'Blog',
                            items: [
                                {text: 'Docker Is Filling Up Your Disk? Clean and Fix It', link: '/blog/docker-disk-full'},
                                {text: 'After SSH Disconnects: nohup, tmux, or systemd?', link: '/blog/ssh-session-persistence'},
                                {text: 'A More Convenient SSH Terminal Management Tool I Built: Termark', link: '/blog/termark-ssh-terminal-workbench'},
                                {text: 'Termark, the SSH Terminal Tool That Feels Better to Use', link: '/blog/wechat-promo-article'},
                                {text: 'Independently Building a Desktop SSH Tool', link: '/blog/desktop-ssh-tool-indie-dev'},
                                {text: 'Termark AI Assistant Design', link: '/blog/termark-ai-design'},
                                {text: 'The Curse of Knowledge in Large Models', link: '/blog/the-curse-of-knowledge-in-ai'}
                            ]
                        }
                    ]
                },
                outlineTitle: 'On This Page',
                docFooter: {
                    prev: 'Previous page',
                    next: 'Next page'
                },
                footer: {
                    message: 'Termark Documentation',
                    copyright
                }
            }
        },
        zh: {
            label: '简体中文',
            lang: 'zh-CN',
            link: '/zh/',
            description: 'Termark 使用文档',
            themeConfig: {
                logo,
                nav: [
                    {text: '使用文档', link: '/zh/usage/sftp-cwd-tracking'},
                    {
                        text: '更新日志',
                        items: [
                            {text: '桌面端更新日志', link: '/zh/changelog'},
                            {text: '移动端更新日志', link: '/zh/mobile-changelog'}
                        ]
                    },
                    {text: '博客', link: '/zh/blog/'},
                    {text: '官方网站', link: 'https://www.termark.app/zh-cn/'}
                ],
                sidebar: {
                    '/zh/usage/': [
                        {
                            text: '使用文档',
                            items: [
                                {text: 'SFTP 目录跟随配置', link: '/zh/usage/sftp-cwd-tracking'},
                                {text: '关键字高亮', link: '/zh/usage/terminal-keyword-highlight'},
                                {text: 'PowerShell 浅色模式显示异常', link: '/zh/usage/powershell-light-theme'},
                                {text: 'Windows 下安全软件误报说明', link: '/zh/usage/windows-virus-warning'},
                                {text: '本地加密与数据恢复说明', link: '/zh/usage/local-encryption'},
                                {text: '数据存储路径', link: '/zh/usage/data-storage-path'},
                            ]
                        }
                    ],
                    '/zh/changelog': [
                        {
                            text: '更新日志',
                            items: [
                                {text: '桌面端更新日志', link: '/zh/changelog'},
                                {text: '移动端更新日志', link: '/zh/mobile-changelog'}
                            ]
                        }
                    ],
                    '/zh/mobile-changelog': [
                        {
                            text: '更新日志',
                            items: [
                                {text: '桌面端更新日志', link: '/zh/changelog'},
                                {text: '移动端更新日志', link: '/zh/mobile-changelog'}
                            ]
                        }
                    ],
                    '/zh/blog/': [
                        {
                            text: '博客',
                            items: [
                                {text: '博客首页', link: '/zh/blog/'},
                                {text: 'Docker 把磁盘吃满了？', link: '/zh/blog/docker-disk-full'},
                                {text: 'SSH 断开后程序还在跑吗？', link: '/zh/blog/ssh-session-persistence'},
                                {text: 'Windows SSH 客户端怎么选？', link: '/zh/blog/windows-ssh-client-guide'},
                                {text: 'SSH 客户端怎么选？', link: '/zh/blog/ssh-client-recommendation'},
                                {text: 'SFTP 客户端怎么选？', link: '/zh/blog/sftp-client-guide'},
                                {text: '手机上可以 SSH 吗？', link: '/zh/blog/can-you-ssh-on-a-phone'},
                                {text: 'SSH 凭据安全吗？', link: '/zh/blog/ssh-credential-security'},
                                {text: 'AI SSH 的安全边界', link: '/zh/blog/termark-ai-design'},
                                {text: '为什么还要做 Termark？', link: '/zh/blog/why-desktop-ssh-tool-in-2026'},
                                {text: '独立开发桌面 SSH 工具', link: '/zh/blog/desktop-ssh-tool-indie-dev'}
                            ]
                        }
                    ]
                },
                outlineTitle: '本页导航',
                docFooter: {
                    prev: '上一页',
                    next: '下一页'
                },
                darkModeSwitchLabel: '外观',
                lightModeSwitchTitle: '切换到浅色模式',
                darkModeSwitchTitle: '切换到深色模式',
                sidebarMenuLabel: '菜单',
                returnToTopLabel: '返回顶部',
                langMenuLabel: '切换语言',
                skipToContentLabel: '跳转到内容',
                footer: {
                    message: 'Termark 使用文档',
                    copyright
                }
            }
        }
    }
})
