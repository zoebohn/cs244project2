import re

def parse_test(numFlows, ecmp):
    averages = []
    num_hosts = 6
    num_runs = 5
    link_capacity = 10000.0
    for i in range(0, num_runs):
        for j in range (0, num_hosts):
            with open("tests/test_host%s_run%s_flows%s_ecmp%s" % (j, i, numFlows, ecmp)) as f:
                lines = f.readlines()
            total = 0
            count = 0
            for line in lines:
                matchObj = re.match(r'(.*)KBytes (.*)Kbits/sec', line)
                if matchObj:
                    total += float(matchObj.group(2))
                    count += 1
            if count != 0:
                average = total / count
                averages.append(average)
    overall_avg = sum(averages) / len(averages)
    percent = overall_avg / link_capacity * 100
    if (ecmp):
        print "average over %s runs with %s hosts with %s flows with ECMP: %s%%" % (num_runs, num_hosts, numFlows, percent)
    else:
        print "average over %s runs with %s hosts with %s flows with 8SP: %s%%" % (num_runs, num_hosts, numFlows, percent)

def main():
    parse_test(1, True)
    parse_test(8, True)
    parse_test(1, False)
    parse_test(8, False)

if __name__ == "__main__":
    main()
