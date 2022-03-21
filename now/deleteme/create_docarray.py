from docarray import DocumentArray

da = DocumentArray.from_files('../../data/deepfashion/**')

# da = DocumentArray(d for d in da if d.uri != '../../data/deepfashion/')

# da.apply(lambda d: d.load_uri_to_image_tensor())
da.apply(lambda d: d.convert_uri_to_image_tensor())

print()
