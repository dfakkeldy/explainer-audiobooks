# Test Fixtures

`echo-export-blocks-v2-golden.json` is a public synthetic fixture for the Echo
`export-blocks` v2 source binding reviewed at Echo commit `f02c045f`. Its root
keys and order (`blocks`, `source`, `version`) and source keys and order
(`epub`, `epubSHA256`) mirror `JSONEncoder` with `.prettyPrinted` and
`.sortedKeys`. It contains no book content and does not record an Echo build,
render, installation, or promotion.
