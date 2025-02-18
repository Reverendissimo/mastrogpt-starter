import re, os, requests as req, json
#MODEL = "llama3.1:8b"
MODEL = "phi4:14b"


FORM = [
  {
    "name": "queen",
    "label": "With a Queen",
    "type": "checkbox",
  },
  {
    "name": "rock",
    "label": "With a Rock",
    "type": "checkbox",
  },
  {
    "name": "knight",
    "label": "With a Knight",
    "type": "checkbox",
  },
  {
    "name": "Bishop",
    "label": "With a Bishop",
    "type": "checkbox",
  },
]


def chat(args, inp):
  host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
  auth = args.get("AUTH", os.getenv("AUTH"))
  url = f"https://{auth}@{host}/api/generate"
  msg = { "model": MODEL, "prompt": inp, "stream": False}
  res = req.post(url, json=msg).json()
  out = res.get("response", "error")
  return  out
 
def extract_fen(out):
  pattern = r"([rnbqkpRNBQKP1-8]+\/){7}[rnbqkpRNBQKP1-8]+"
  fen = None
  m = re.search(pattern, out, re.MULTILINE)
  if m:
    fen = m.group(0)
  return fen

def puzzle(args):
  out = "If you want to see a chess puzzle, type 'puzzle'. To display a fen position, type 'fen <fen string>'."
  inp = args.get("input", "")
  res = {}


  if inp == "puzzle":
    #inp = "generate a chess puzzle in FEN format"
    #out = chat(args, inp)
    #fen = extract_fen(out)
    #if fen:
    #   print(fen)
    #   res['chess'] = fen
    #else:
    res['form'] = FORM
  elif type(inp) is dict and "form" in inp:
      data = inp["form"]
      puzzle_template = f"""
      Generate a chess puzzle in FEN format
      """
      req_pcs = []
      tail = " making sure the following chess pieces are present:"
      #puzzle_template += " --- "
      for field in data.keys():
        #puzzle_template += f" {field} {data[field]} "
        if data[field] == "true":
          req_pcs.append(field)

      if len(req_pcs) > 0:
        puzzle_template += str(f"{tail}")
        for req_p in req_pcs:
          puzzle_template += str(f"{req_p}, ")
      
      out = chat(args, puzzle_template)
      fen = extract_fen(out)
      if fen:
        res['chess'] = fen

  elif inp.startswith("fen"):
    fen = extract_fen(inp)
    if fen:
       out = "Here you go."
       res['chess'] = fen
  elif inp != "":
    out = chat(args, inp)
    fen = extract_fen(out)
    print(out, fen)
    if fen:
      res['chess'] = fen

  res["output"] = out
  return res
