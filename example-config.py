
# Example direg configuration

directories = [

        {
            'path' : '~/tmp/podcasts/single',
            'test': 'is_day_of_week',
            'dow': '1,2,3,4,5,' ,
            'solution': 'do_nothing'
        },

        # {
        #     'path' : '~/tmp/podcasts/multi/*',
        #     'test': 'max_size',
        #     'max_size': '100GB'
        # }

    ]

