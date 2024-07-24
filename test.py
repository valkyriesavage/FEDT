from decorator import fedt_fabricate


@fedt_fabricate(instruction="Do the thing.")
def foo():
    print("AAA")
