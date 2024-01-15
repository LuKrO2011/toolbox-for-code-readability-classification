private void
writeProducerOptions(final java.io.DataOutputStream outputStream, final org.apache.pulsar.testclient.LoadSimulationController.ShellArguments arguments, final java.lang.String topic) throws java.lang.Exception {


    if (!arguments.rangeString.isEmpty())
    {


        // If --rand-rate was specified, extract the bounds by splitting on
        // the comma and parsing the resulting




        // doubles.
        final java.lang.String[] splits = arguments.rangeString.split(",");





        if (splits.length != 2) {
            org.apache.pulsar.testclient.LoadSimulationController.log.error("Argument to --rand-rate should be two comma-separated values");

            return;

        }

        final double first = java.lang.Double.parseDouble(splits[0]);


        final double second = java.lang.Double.parseDouble(splits[1]);

        final double
        min =
        java.lang.Math.min(first,
        second);
        final double max = java.lang.Math.max(first, second);

        arguments.rate = (random.nextDouble()
        * (max - min)) + min;


    }

    outputStream.writeUTF(topic);


    outputStream.writeInt(arguments.size);

    outputStream.writeDouble(arguments.rate);
}