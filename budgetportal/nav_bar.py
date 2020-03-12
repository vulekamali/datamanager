def get_items(financial_year):
    return [
        {"id": "homepage", "title": "Home", "url": "/"},
        {
            "id": "departments",
            "title": "Department Budgets",
            "url": "/%s/departments" % financial_year,
        },
        {
            "id": "learning-centre",
            "title": "Learning",
            "url": "/videos",
            "subLinks": True,
            "children": [
                {"title": "Videos", "id": "videos", "url": "videos"},
                {"title": "Glossary", "id": "glossary", "url": "glossary"},
                {"title": "Resources", "id": "resources", "url": "resources"},
                {"title": "Dataset Guides", "id": "guides", "url": "guides"},
            ],
        },
        {
            "id": "infrastructure",
            "title": "Infrastructure",
            "url": None,
            "is_dropdown": True,
            "children": [
                {
                    "title": "Featured major projects",
                    "url": "infrastructure-projects/",
                    "id": "national",
                },
                {
                    "title": "Government department projects",
                    "url": "infrastructure-projects/provincial/",
                    "id": "provincial",
                },
            ],
        },
        {"id": "datasets", "title": "Data and Analysis", "url": "/datasets"},
        {
            "id": "about",
            "title": "About",
            "url": "/about",
            "align": "right",
            "subLinks": True,
            "children": [
                {
                    "title": "Background",
                    "url": "about#background",
                    "connected": "background",
                },
                {
                    "title": "Development",
                    "url": "about#development",
                    "connected": "development",
                },
                {
                    "title": "Project Status",
                    "url": "about#project-status",
                    "connected": "project-status",
                },
                {
                    "title": "Your Contribution",
                    "url": "about#your-contribution",
                    "connected": "your-contribution",
                },
                {"title": "Contacts", "url": "about#contacts", "connected": "contacts"},
                {
                    "title": "Media & Other Information",
                    "url": "about#media-and-other-information",
                    "connected": "media-and-other-information",
                },
                {
                    "title": "Information for Developers and Data Scientists",
                    "url": "about#data-scientists",
                    "connected": "data-scientists",
                },
            ],
        },
        {"id": "faq", "title": "FAQ", "url": "/faq", "align": "right"},
    ]
