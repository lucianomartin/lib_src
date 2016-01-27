import xmostest

supported_sr = (44100, 48000, 88200, 96000, 176400, 192000)
num_in_samps = 256

def runtest():
    
    simargs_ssrc = ""

    resources = xmostest.request_resource("xsim")
    
#    xmostest.build("ssrc_test", env = {})
#    xmostest.set_test_result("lib_src", "ssrc_tests", "ssrc_smoke_test", "ssrc_test"

    test_files = ("output_ch0.dat", "output_ch1.dat")

    golden_files = ("ssrc_test/expected/s1k_0dB_192_44_256.expect", "ssrc_test/expected/s1k1_0dB_192_44_256.expect")
    tester = FileComparisonTester(test_files, golden_files, "lib_src", "ssrc_tests", "ssrc_test", {}, regexp = False, ignore=[])

    args = "-i ./input_sines/s1k_0dB_192.dat ./input_sines/s1k_0dB_176.dat -o output_ch0.dat output_ch1.dat"

    len_test_files = len(test_files)
    len_golden_files = len(golden_files)
    
    if isinstance(test_files, str):
        len_test_files = 1
    if isinstance(golden_files, str):
        len_golden_files = 1
    if (len_test_files != len_golden_files):
        print("ERROR: %d test file(s) specified and %d golden file(s)" % (len_test_files), len_golden_files))
        xmostest.set_test_result(product, group, test, config, result=False, output = "Number of inout and output files does not match", env = env)
    print("Found %d audio channels to process" % len(test_files))

    for input_sr in supported_sr:
        for output_sr in supported_sr:
            if (input_sr == 192000) and (output_sr == 44100):
                print ('Running test SR input = %d, output = %d' % (input_sr, output_sr))
                args_file = open("xsim.args", 'wt')
                args += " -f " + str(input_sr) + " -g " + str(output_sr) + " -n " + str(num_in_samps)
                args_file.write(args)
    args_file.close()
    xmostest.run_on_simulator(resources["xsim"],
                              "./ssrc_test/bin/ssrc_test.xe",
                              simargs=[simargs_ssrc],
                              tester=tester)
            else:
                print ('NOT running test SR input = %d, output = %d' % (input_sr, output_sr))




class FileComparisonTester(xmostest.Tester):
    """
        This tester will compare two files and pass a test if
        the output matches
        """
    
    def __init__(self, input, golden, product, group, test, config = {}, env = {},
                 regexp = False, ignore=[]):
        super(FileComparisonTester, self).__init__()
        self.register_test(product, group, test, config)
        self._golden = golden
        self._input = input
        self._test = (product, group, test, config, env)
        self._regexp = regexp
        self._ignore = ignore
    
    def record_failure(self, failure_reason):
        # Append a newline if there isn't one already
        if not failure_reason.endswith('\n'):
            failure_reason += '\n'
        self.failures.append(failure_reason)
        print ("ERROR: %s" % failure_reason), # Print without newline
        self.result = False
    
    def run(self, output):
        input_files = self._input
        index = 0
        for input_file_name in input_files:
            print("Opening input file %s" % input_file_name)
            input_file = open(input_file_name, "r")
            test_result = [x.strip() for x in input_file.readlines()]
            
            (product, group, test, config, env) = self._test
            regexp = self._regexp

            golden_file_name = self._golden[index]
            print("Opening golden file %s" % golden_file_name)
            golden = open(golden_file_name, "r")
            expected = [x.strip() for x in golden.readlines()]
            
            if expected[0].strip()=='':
                expected = expected[1:]
            if expected[-1].strip()=='':
                expected = expected[:-1]
            
            self.result = True
            self.failures = []
            line_num = -1
            for i in range(len(test_result)):
                ignore = False
                for p in self._ignore:
                    if re.match(p,test_result[i].strip()):
                        ignore = True
                        break
                if ignore:
                    continue
                line_num += 1
                
                #print("line_num=%d, result=%s, line=%s" % (line_num, self.result, test_result[i].strip()))
                if line_num >= len(expected):
                    self.record_failure("Length of expected test result less than expected file")
                    break
                
                if regexp:
                    match = re.match(expected[line_num]+"$", test_result[i].strip())
                else:
                    match = expected[line_num] == test_result[i].strip()
                
                if not match:
                    self.record_failure(("Line %d of test result does not match expected file\n"+
                                         "  Expected     : %s\n"+
                                         "  Actual input : %s")
                                        % (line_num,
                                           expected[line_num].strip(),
                                           test_result[i].strip()))
        
            if (len(expected) > line_num + 1):
                self.record_failure("Length of expected file greater than test result")
                test_result = {'test_result':''.join(test_result)}
            if not self.result:
                test_result['failures'] = ''.join(self.failures)
            index += 1
        xmostest.set_test_result(product, group, test, config, self.result,
                             output = test_result, env = env)
