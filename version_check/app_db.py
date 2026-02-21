apps = [
    {
        "name": "Guacamole",
        "github_tag_url": "apache/guacamole-server",
        "docker_url": "guacamole/guacamole",
    },
    {"name": "Django", "github_tag_url": "django/django"},
    {"name": "Sonarr", "github_url": "Sonarr/Sonarr", "docker_url": "linuxserver/sonarr"},
    {"name": "Traefik", "github_url": "traefik/traefik", "docker_url": "library/traefik"},
    {
        "name": "Vaultwarden",
        "github_url": "dani-garcia/vaultwarden",
        "docker_url": "vaultwarden/server",
    },
    {"name": "Radarr", "github_url": "Radarr/Radarr", "docker_url": "linuxserver/radarr"},
    {"name": "K3S", "github_url": "k3s-io/k3s"},
    {"name": "HomeAssistant", "github_url": "home-assistant/core"},
    {
        "name": "Debian",
        "url": "https://www.debian.org/News/",
        "index_pattern": '<tt>\\[.+?\\]</tt>.+?<strong><a href="(.+?)">(.+?)</a>',
        "page_pattern": '<div id="content">.+?(.+?)<div id="footer">',
    },
    {
        "name": "Proxmox",
        "url": "https://www.proxmox.com/en/news/press-releases",
        "index_pattern": '<a href="/en/about/press-releases(/.+?)".*?>(.+?)</a>',
        "page_pattern": '<div class="custom-article-text">(.*?)</div>',
    },
]
