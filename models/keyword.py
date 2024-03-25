import spacy
import json

def extract_keywords_and_save(text_path):
    nlp = spacy.load(r'Spacy-tuned')

    with open(text_path, encoding='utf-8') as f:
        text = f.read()
        print(f"Received Text")

    doc = nlp(text)

    output_data = {
        "job_title": "",
        "must_have": [],
        "good_to_have": [],
        "locations": [],
        "experiences": "",
    }

    seen_skills = set()
    for ent in doc.ents:
        if ent.text not in seen_skills:
            if ent.label_ == "MUST HAVE":
                output_data["must_have"].append(ent.text)
            elif ent.label_ == "GOOD TO HAVE":
                output_data["good_to_have"].append(ent.text)
            elif ent.label_ == "LOCATION":
                output_data["locations"].append(ent.text)
            elif ent.label_ == "EXPERIENCE":
                output_data["experiences"] = ent.text
            elif ent.label_ == "JOB TITLE":
                output_data['job_title'] = ent.text

            seen_skills.add(ent.text)

    # Define final_load after the loop
    final = json.dumps(output_data, indent=4)
    final_load = json.loads(final)

    return final_load