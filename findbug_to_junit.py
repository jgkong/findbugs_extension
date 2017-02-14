#!/usr/bin/env python

import sys

try:
  from lxml import etree
  #print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    #print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      #print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        #print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          #print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")


class jUnitXML(object):

    def __init__(self):
        self.init_tree()

    def init_tree(self):
        self.root = etree.Element('testsuites')
        self.suites = {}

    def add_suite(self, suite_id, name):
        if suite_id in self.suites:
            return self.suites[suite_id]
        else:
            suite = etree.SubElement(self.root, 'testsuite')
            suite.attrib['id'] = suite_id
            suite.attrib['name'] = name
            self.suites[suite_id] = suite
            return suite

    def add_case(self, suite_id, suite_name, case_id, name):
        suite = self.add_suite(suite_id, suite_name)
        case = etree.SubElement(suite, 'testcase')
        case.attrib['id'] = case_id
        case.attrib['name'] = name
        return case

    def add_failure(self, suite_id, suite_name, case_id, case_name,
            type_severity, msg, lines):
        """
        Args:
            suite_id
            suite_name: Category of tests (testsuite:name)
            case_id
            case_name: Name of test (testcase:name)
            type_severity: severity (e.g. WARNING, ERROR)
            msg: detailed message of failure
            lines: stack trace of failure
        """
        case = self.add_case(suite_id, suite_name, case_id, case_name)
        failure = etree.SubElement(case, 'failure')
        failure.attrib['type'] = type_severity
        failure.attrib['message'] = msg
        failure.text = '\n'.join(lines)
        return failure

    def show(self):
        print('<?xml version="1.0" encoding="UTF-8"?>')
        print(etree.tostring(self.root))

    def dump(self):
        return '\n'.join([
                '<?xml version="1.0" encoding="UTF-8"?>\n',
                etree.tostring(self.root),
                ])

def findbugs_junit(infile, outfile):
    out = jUnitXML()

    try:
        tree = etree.parse(infile)
    except Exception as e:
        raise Exception('{}\nCannot read from xml: {}'.format(e.message, infile))
    bugs = tree.findall('./BugInstance')

    for bug in bugs:
        details = [ n.text for n in bug.findall('.//Message') ]

        msgs = {}
        for msg_type in ['Short', 'Long']:
            msg = bug.find('{}Message'.format(msg_type))
            msgs[msg_type] = bug.attrib['type'] if (msg is None) else msg.text


        cls = bug.find('Class')

        out.add_failure(
            bug.attrib['category'],
            bug.attrib['category'],
            bug.attrib['abbrev'],
            msgs['Short'],
            'WARNING',
            msgs['Long'],
            details,
            #[ bug.find('LongMessage').text, ]
        )

    try:
        with open(outfile, 'w') as fp:
            fp.write(out.dump())
    except Exception as e:
        raise Exception('{}\nCannot write file: {}'.format(e.message, outfile))

def main():
    if len(sys.argv) < 3:
        print('Usage: {} infile.xml outfile.xml'.format(sys.argv[0]))
        return

    findbugs_junit(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()

