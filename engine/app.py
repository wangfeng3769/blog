# coding=utf-8

__all__ = ["start"]


from tornado.web import Application as torandoApplication, RedirectHandler, ErrorHandler



class Application(torandoApplication):
    # 
    # Tornado Application
    # 
    def __call__(self, request):
        # 
        # 在处理错误前，记录请求信息。
        # 
        handler = super(Application, self).__call__(request)
        print " *  URI: {0:<15} {1}".format(type(handler).__name__, request.uri)
        return handler



class AppEngine(object):
    #
    # 基于 Tornado 封装
    # 
    # 1. 自动搜索相关模块，查找处理方法，并封装成 RequestHandler 类型。
    # 2. 依据配置决定是否启用多进程模式。
    # 
    def _get_handlers(self):
        # 
        # 获取 engine.web 和 action 中的所有 RequestHandler。
        # 
        from inspect import isclass
        from tornado.web import RequestHandler
        from utility import get_module_members, get_package_members
        import web, action

        handlers = []

        # 动态载入处理器。
        predicate = lambda m: isclass(m) and issubclass(m, RequestHandler) and hasattr(m, "action")
        handlers.extend(get_module_members(web, predicate))
        handlers.extend(get_package_members(action, predicate))

        # 排序
        handlers.sort(key = lambda h: h.action.order)

        # 显示载入信息。
        for h in handlers: 
            print " + Load: [{0:>3}] {1:5} {2:<20}  {3}".format(h.action.order, h.action.method, h.action.name, h.action.url)

        return map(lambda h: (h.action.url, h), handlers)


    def _get_settings(self):
        # 
        # 返回 Tornado Application 配置。
        # 
        return dict(
            debug = settings.DEBUG,
            gzip = settings.GZIP,
            login_url = settings.LOGIN,
            template_path = settings.TEMPLATE,
            static_path = settings.STATIC,
            cookie_secret = settings.SECRET,
            xsrf_cookies = not settings.DEBUG,
        )


    def run(self):
        # 
        # 启动 Tornado HTTP server。
        # 
        # 当 DEBUG = False 时，启动多进程模式。
        # 当 DEBUG = True 时，修改的模块自动重载。
        # 
        from os import getpid
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop

        app = Application(self._get_handlers(), **self._get_settings())
        server = HTTPServer(app)
        port = settings.PORT

        if settings.DEBUG:
            server.listen(port)
            IOLoop.instance().start()
        else:
            # 多进程模式
            server.bind(port)
            server.start(0)
            print " * Sub Process: {0}".format(getpid())

        IOLoop.instance().start()            



def start():
    # 
    # 启动 AppEngine。
    # 
    from os import getpid
    print "AppEngine starting... (pid:{0}, port:{1})".format(getpid(), settings.PORT)

    AppEngine().run()





