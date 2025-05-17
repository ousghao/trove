# Oracle Middleware options
oracle_middleware_group = cfg.OptGroup('oracle_middleware',
                                      title='Oracle Middleware Options')

oracle_middleware_opts = [
    cfg.StrOpt('oracle_middleware_url',
               default='http://localhost:8000',
               help='URL of the Oracle middleware service'),
]

CONF.register_group(oracle_middleware_group)
CONF.register_opts(oracle_middleware_opts, group=oracle_middleware_group) 