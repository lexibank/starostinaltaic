from pathlib import Path
import lingpy as lp

from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar
from pylexibank import Concept, Language, FormSpec
import attr

@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    IDInSource = attr.ib(default=None)
    Family = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = 'starostinaltaic'
    concept_class = CustomConcept
    language_class = CustomLanguage
    form_spec = FormSpec(
            missing_data=("–", "-"),
            brackets={"(": ")", "[": "]", "{": "}"},
            first_form_only=True,
            separators = (";", "/", "~", ","),
            replacements=[] 
            )

    def cmd_makecldf(self, args):
    
        concepts = {}

        for concept in self.conceptlists[0].concepts.values():
            idx = '{0}_{1}'.format(concept.number, slug(concept.english))
            args.writer.add_concept(
                    ID=idx,
                    Number=concept.number,
                    Name=concept.english,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss,
                    )
            concepts[concept.english] = idx
            concepts[concept.number] = idx
        
        
        languages = args.writer.add_languages(
                lookup_factory="IDInSource", id_factory=lambda x: slug(x['Name']))
        
        args.writer.add_sources()
        loanid = 5000
        data = self.raw_dir.read_csv("alt.csv", dicts=True)
        for row in progressbar(data[1:], desc="cldfify"):
            for language, lid in languages.items():
                entry = row[language]
                cogid = row[language+"NUM"]
                concept = concepts[row["NUMBER"]]
                loan = True if int(cogid) < 0 else False
                if loan:
                    this_cogid = loanid
                    loanid += 1
                else:
                    this_cogid = cogid
                if entry.strip():
                    lexeme = args.writer.add_forms_from_value(
                            Language_ID=lid,
                            Parameter_ID=concept,
                            Value=entry,
                            Cognacy=this_cogid,
                            Loan=loan,
                            Source="Starostin2005"
                            )[0]
                    args.writer.add_cognate(
                            lexeme=lexeme,
                            Cognateset_ID=cogid,
                            Cognate_Detection_Method="expert",
                            Source="Starostin2005"
                            )
       
