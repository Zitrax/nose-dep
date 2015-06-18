from nose.plugins import Plugin


class NoseDep(Plugin):
    #enabled = False
    name = "nosedep"
    score = 100

    def __init__(self):
        super(NoseDep, self).__init__()

    def options(self, parser, env):
        print("OPT")
        super().options(parser, env)

    def configure(self, options, conf):
        print("CONF")
        super().configure(options, conf)
        if not self.enabled:
            print("NOT")
        else:
            print("YES")

    def prepareTest(self, test):
        print("PT {}".format(test))
        print(test._tests)
        all_tests = []
        for t in test._tests:
            for tt in t:
                all_tests.append(tt)
        test._tests = (t for t in reversed(all_tests))
        for t in test._tests:
            print("1", t)
        return test

    def makeTest(self, obj, parent):
        print("MT {} {}".format(obj, parent))

    def addSuccess(self, test):
        print("OKI DOKI")

    def loadTestsFromDir(self, path):
        print("HERE1")

    def loadTestsFromModule(self, module, path=None):
        print("HERE2 {}".format(module))

    def loadTestsFromName(self, name, module=None, importPath=None):
        print("HERE3 {}".format(name))

    def loadTestsFromNames(self, names, module=None):
        print("HERE4 {}".format(names))
        #from nose import loader
        #l = loader.TestLoader()
        #tmp = l.loadTestsFromNames(names, module)
        #print(tmp)
        #return tmp

    def loadTestsFromFile(self, filename):
        print("HERE5")

    def loadTestsFromTestCase(self, cls):
        print("HERE6")

    def loadTestsFromTestClass(self, cls):
        print("HERE7")