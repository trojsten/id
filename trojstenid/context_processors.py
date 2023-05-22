import trojstenid


def version(request):
    return {"ID_VERSION": trojstenid.VERSION}
