import {defineConfig} from 'vitepress'

const logo = {
    src: '/logo.svg',
    alt: 'Termark'
}

const copyright = 'Copyright © 2026 Termark'

export default defineConfig({
    lang: 'en-US',
    title: 'Termark',
    description: 'Termark documentation',
    head: [
        ['link', {rel: 'icon', type: 'image/svg+xml', href: '/logo.svg'}]
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
                    {text: 'Changelog', link: '/changelog'},
                    {text: 'Blog', link: '/blog/termark-ssh-terminal-workbench'}
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
                                {text: 'Changelog', link: '/changelog'}
                            ]
                        }
                    ],
                    '/blog/': [
                        {
                            text: 'Blog',
                            items: [
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
                    {text: '博客', link: '/zh/blog/termark-ssh-terminal-workbench'}
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
                                {text: '如果你经常连服务器，可以试试 Termark', link: '/zh/blog/termark-ssh-terminal-workbench'},
                                {text: '我做了一个更顺手的 SSH 终端管理工具：Termark', link: '/zh/blog/wechat-promo-article'},
                                {text: '独立开发一个桌面 SSH 工具：最麻烦的不是写代码', link: '/zh/blog/desktop-ssh-tool-indie-dev'},
                                {text: 'Termark AI 助手设计：我为什么没有做一个"全自动运维 Agent', link: '/zh/blog/termark-ai-design'},
                                {text: '大模型里的“知识的诅咒”', link: '/zh/blog/the-curse-of-knowledge-in-ai'}
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
