
# Example direg configuration

directories = [

        {
            'path' : '~/tmp/podcasts/program',
            'test': 'max_count',
            'max_count':100
        },

        {
            'path' : '~/tmp/podcasts/multi/*',
            'test': 'max_size',
            'max_size': '100GB'
        }

    ]

