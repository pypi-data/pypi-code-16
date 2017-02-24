def generate_method(methodName, arguments, localVars):
    methodName = methodName.upper()

    indentLength = len(methodName) + 6
    indent = "%-" + str(indentLength) + "s"

    freeIndent = indent % ""
    callerLabelIndent = indent % ("CALL" + methodName)
    methodLabelIndent = indent % methodName

    result = ""

    # Start building the caller block
    result += "%sADD R6, R6, -%d ; Create room for the arguments\n" % (callerLabelIndent, arguments)

    for i in xrange(arguments):
        result += "%sSTR R0, R6, %d ; Store R0 as argument %d\n" % (freeIndent, i, i + 1)

    result += "%sJSR %s ; Call the method\n" % (freeIndent, methodName)

    result += "%sLDR R0, R6, 0 ; Fetch return value into R0\n" % freeIndent

    result += "%sADD R6, R6, %d ; Remove the stack frame\n\n" % (freeIndent, arguments + 1)

    # Start building the method block itself
    result += "%sADD R6, R6, -3 ; Reserve 3 spaces (return value, return address, old frame pointer)\n" % methodLabelIndent

    result += "%sSTR R7, R6, 1 ; Store the return address\n" %  freeIndent

    result += "%sSTR R5, R6, 0 ; Store the old frame pointer\n" % freeIndent

    result += "%sADD R5, R6, -1 ; Set frame pointer to where variables begin\n" % freeIndent

    result += "%sADD R6, R6, %d ; Create room for variables\n" % (freeIndent, -1 * localVars)

    if (arguments > 0):
        result += "\n%s; Addresses of arguments:\n" % (freeIndent)

        for i in xrange(arguments):
            result += "%s; R5, %d: arg%d\n" % (freeIndent, 4+i, i+1)

    if (localVars > 0):
        result += "\n%s; Addresses of variables:\n" % (freeIndent)

        for i in xrange(localVars):
            result += "%s; R5, %d: var%d\n" % (freeIndent, -i, i+1)

    ending = """
{0}; Do what you want here

{0}STR R0, R5, 3 ; Store result in return value

{0}ADD R6, R5, 3 ; Move the stack pointer to our return value
{0}LDR R7, R5, 2 ; Pull return address for RET instr
{0}LDR R5, R5, 1 ; Restore old frame pointer

{0}RET ; Exit method
    """

    result += ending.format(freeIndent)

    return result