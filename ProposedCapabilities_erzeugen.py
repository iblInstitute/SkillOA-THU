# Laden ont
from rdflib import Graph
from pathlib import Path
from rdflib import Graph, URIRef, RDF, Namespace, Literal
from rdflib.namespace import XSD
import pandas as pd
import os
# Initialisierung

def reload_graph():
    ont_iri = "http://www.semanticweb.org/SkillOA/2025/3/KBI/"
    ont_ir = Namespace(ont_iri)
    class_pr = Namespace(f"{ont_iri}class_")
    op_pr = Namespace(f"{ont_iri}op_")
    dp_pr = Namespace(f"{ont_iri}dp_")

    ontology_path = Path(r"C:\Users\Alexander Verkhov\Downloads\KB1_v0.5.ttl")
    
    if not ontology_path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {ontology_path}")

    g = Graph()

    # Statt file=..., den Inhalt als String lesen
    ttl_text = ontology_path.read_text(encoding="utf-8")
    g.parse(data=ttl_text, format="turtle")

    return ont_ir, class_pr, op_pr, dp_pr, ontology_path, g
#reload_graph()
ont_iri,class_prefix,op_prefix,dp_prefix,ontology_path,g = reload_graph()

def query_first_skill():
    #Hier wird davon ausgegangen, dass das genau ein Skill ist
    _,class_prefix,_,dp_prefix,_,g = reload_graph()
    #skill_in = "TestSkill5"
    query = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX dp: <{dp_prefix}>
        SELECT DISTINCT ?skill WHERE {{
        # Startpunkt der Kette
        ?skill a cl:Skill;
            dp:firstSkill True .
        }}
        """
    relation_results = g.query(query)
    #res1 = len(relation_results)
    for row in relation_results:
        return str(row.skill)  # gibt die URI als String zurück

    # Falls kein Ergebnis gefunden wurde
    return None

def query_last_skill():
    #Hier wird davon ausgegangen, dass das genau ein Skill ist
    _,class_prefix,_,dp_prefix,_,g = reload_graph()
    #skill_in = "TestSkill5"
    query = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX dp: <{dp_prefix}>
        SELECT DISTINCT ?skill WHERE {{
        ?skill a cl:Skill;
            dp:lastSkill True .
        }}
        """
    relation_results = g.query(query)
    #print(query)
    #res1 = len(relation_results)
    for row in relation_results:
        return str(row.skill)  # gibt die URI als String zurück

    # Falls kein Ergebnis gefunden wurde
    return None


def find_skill_for_service_request_param(dp_uri,dp_value):
        ont_iri,class_prefix,op_prefix,_,_,g = reload_graph()
    # Skills finden, die dieselbe dataProp mit derselben datavalue haben
    # Dann ist klar, dass einer von diesen Skills ausgeführt werden muss, also dass alle Skill-Ketten einen dieser Skills beinhalten müssen.
        querySkillsearch = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX op: <{op_prefix}>
        PREFIX ont: <{ont_iri}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        #PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT DISTINCT ?skill ?ParamIndiv ?property WHERE {{
        ?skill a cl:Skill;
            ?property ?ParamIndiv .
        ?property rdfs:subPropertyOf op:offersSkillParameter.
        ?ParamIndiv <{dp_uri}> "{dp_value}".
        }}
        """
        #print(querySkillsearch)
        relation_results = g.query(querySkillsearch)
        df = pd.DataFrame(relation_results, columns=[str(var) for var in relation_results.vars])
        pd.set_option('display.max_colwidth',None)
        return df
        #print(df)

# Abfrage Service Parameter
def query_service_parameters(service_req_uri):
    ont_iri,class_prefix,op_prefix,_,_,g = reload_graph()
    query = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX op: <{op_prefix}>
        PREFIX ont: <{ont_iri}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?property ?ParamIndiv ?dataProp ?datavalue (DATATYPE(?datavalue) as ?datatype) WHERE {{
        # Startpunkt der Kette
        <{service_req_uri}> a cl:ServiceRequest;
            ?property ?ParamIndiv .
        ?property rdfs:subPropertyOf op:hasRequestedServiceParameter.
        ?ParamIndiv ?dataProp ?datavalue.
        ?dataProp a owl:DatatypeProperty.
        }}
        """

        #print(class_prefix)
        #print(Skill_query)

    #print(query)
    relation_results = g.query(query)
    #res1 = len(relation_results)
    df = pd.DataFrame(relation_results, columns=[str(var) for var in relation_results.vars])
    return df



def query_service_parameters2(service_req_uri):
    ont_iri,class_prefix,op_prefix,_,_,g = reload_graph()
    query = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX op: <{op_prefix}>
        PREFIX ont: <{ont_iri}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?skill ?property ?ParamIndiv ?dataProp ?datavalue (DATATYPE(?datavalue) as ?datatype) WHERE {{
        # Startpunkt der Kette
        <{service_req_uri}> a cl:ServiceRequest;
            ?property ?ParamIndiv .
        ?property rdfs:subPropertyOf op:hasRequestedServiceParameter.
        ?ParamIndiv ?dataProp ?datavalue.
        ?dataProp a owl:DatatypeProperty.
        }}
        """

        #print(class_prefix)
        #print(Skill_query)

    #print(query)
    relation_results = g.query(query)
    #res1 = len(relation_results)
    df = pd.DataFrame(relation_results, columns=[str(var) for var in relation_results.vars])
    
   # print(df)
    #df["property"] = df["property"].str.replace("ParameterOut", "ParameterIn", regex=False)
    #pd.set_option('display.max_colwidth',None)
    all_skills_df = pd.DataFrame()
    for _, row in df.iterrows():
        dp_uri = str(row['dataProp'])
        dp_value = str(row['datavalue'])
        dfskills = find_skill_for_service_request_param(dp_uri,dp_value)
        #print(dfskills)
        if not dfskills.empty:
            all_skills_df = pd.concat([all_skills_df, dfskills], ignore_index=True)
        #dp_datatype = str(row['datatype'])
        #print(dp_uri, dp_value)
        #print(class_prefix)
        #print(Skill_query)

    #print(query)
    #return dfskills
    return all_skills_df


import json

def query_skill_all_skill_information(skill_uri):
    ont_iri, class_prefix, op_prefix, dp_prefix, _, g = reload_graph()

    # 1. Parameter-Abfrage
    query_params = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX op: <{op_prefix}>
        PREFIX ont: <{ont_iri}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?property ?ParamIndiv ?dataProp ?datavalue WHERE {{
            <{skill_uri}> a cl:Skill;
                ?property ?ParamIndiv.
            ?property rdfs:subPropertyOf op:offersSkillParameter.
            FILTER regex(str(?property), "Parameter")
            ?ParamIndiv ?dataProp ?datavalue.
            ?dataProp a owl:DatatypeProperty.
        }}
    """
    results_params = g.query(query_params)

    # 2. ParallelToAllSkills (Data Property)
    query_parallel_to_all = f"""
        PREFIX cl: <{class_prefix}>
        PREFIX dp: <{dp_prefix}>
        SELECT ?flag WHERE {{
            <{skill_uri}> dp:isExecutableParallelToAllSkills ?flag.
        }}
    """
   # print(query_parallel_to_all)
    results_flag = g.query(query_parallel_to_all)
    is_parallel_to_all = any(str(row.flag).lower() == "true" for row in results_flag)

    # 3. Falls nicht parallel zu allen Skills → normale parallele Skills abfragen
    parallel_skills = "ParallelToAllSkills" if is_parallel_to_all else []
    
    if not is_parallel_to_all:
        query_parallel = f"""
            PREFIX cl: <{class_prefix}>
            PREFIX op: <{op_prefix}>
            PREFIX ont: <{ont_iri}>
            SELECT DISTINCT ?parallelSkill WHERE {{
                <{skill_uri}> a cl:Skill;
                    op:hasParallelSkill ?parallelSkill.
            }}
        """
        results_parallel = g.query(query_parallel)
        parallel_skills = [str(row.parallelSkill) for row in results_parallel]

    # 4. Parameter-Daten sammeln
    param_list = []
    for row in results_params:
        param_list.append({
            "position_in_Capability": None,
            "property": str(row.property),
            "ParamIndiv": str(row.ParamIndiv),
            "dataProp": str(row.dataProp),
            "datavalue": str(row.datavalue)
        })

    # 5. Struktur erstellen
    result = [{
        "skill": str(skill_uri),
        "parameters": param_list,
        "hasParallelSkill": parallel_skills
    }]

    return json.dumps(result, indent=2)

def is_position_in_range(target_pos_str, range_def_str):
    def parse_vector(vec_str):
        return list(map(float, vec_str.strip("[]").split(";")))

    def in_single_range(pos, start, end):
        return all(s <= p <= e for p, s, e in zip(pos, start, end))

    # Parse Zielposition
    target = parse_vector(target_pos_str)

    # mögliche mehrere Ranges mit '+' splitten
    ranges = range_def_str.split("+")
    
    for r in ranges:
        parts = r.split("];[")
        if len(parts) == 1:
            # Nur ein Punkt
            point = parse_vector(parts[0])
            if target == point:
                return True
        elif len(parts) == 2:
            # Intervall
            start = parse_vector(parts[0])
            end = parse_vector(parts[1])
            if in_single_range(target, start, end):
                return True
        else:
            raise ValueError("Ungültiges Range-Format")
    
    return False

def ranges_overlap(range1_str, range2_str):
    def parse_vector(vec_str):
        return list(map(float, vec_str.strip("[]").split(";")))

    def parse_range(range_str):
        # Einzelpunkt-Check
        if "[" in range_str and "]" in range_str and ";" not in range_str:
            vec = parse_vector(range_str)
            return [(vec, vec)]  # Punktbereich
        # Richtiger Bereich
        parts = range_str.split(";")
        if len(parts) != 2:
            raise ValueError(f"Ungültiger Bereich: {range_str}")
        start = parse_vector(parts[0])
        end = parse_vector(parts[1])
        # Min/Max absichern
        s = [min(a, b) for a, b in zip(start, end)]
        e = [max(a, b) for a, b in zip(start, end)]
        return [(s, e)]

    def ranges_intersect(start1, end1, start2, end2):
        return all(not (e1 < s2 or e2 < s1) for s1, e1, s2, e2 in zip(start1, end1, start2, end2))

    # Zerlegen beider Range-Strings (enthalten +)
    ranges1 = []
    for r in range1_str.split("+"):
        ranges1.extend(parse_range(r))

    ranges2 = []
    for r in range2_str.split("+"):
        ranges2.extend(parse_range(r))

    # Kombinationen vergleichen
    for (s1, e1) in ranges1:
        for (s2, e2) in ranges2:
            if ranges_intersect(s1, e1, s2, e2):
                return True

    return False
#Überprüfen, welche Parameter ein Skill auf Output-Seite hat
#Nächster Skill wird nur mit den Werten verglichen, die ein Skill hat
def query_skill_parameters_out(skill_uri):
    ont_iri,class_prefix,op_prefix,_,_,g = reload_graph()
    #skill_in = "TestSkill5"
    query = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX op: <{op_prefix}>
        PREFIX ont: <{ont_iri}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?property ?ParamIndiv ?dataProp ?datavalue WHERE {{
        # Startpunkt der Kette
        <{skill_uri}> a cl:Skill;
            ?property ?ParamIndiv .
        ?property rdfs:subPropertyOf op:offersSkillParameter.
        FILTER regex(str(?property), "ParameterOut")
        ?ParamIndiv ?dataProp ?datavalue.
        ?dataProp a owl:DatatypeProperty.
        }}
        """

        #print(class_prefix)
        #print(Skill_query)

    #print(query)
    relation_results = g.query(query)
    #res1 = len(relation_results)
    df = pd.DataFrame(relation_results, columns=[str(var) for var in relation_results.vars])
    #df["property"] = df["property"].str.replace("ParameterOut", "ParameterIn", regex=False)
    #pd.set_option('display.max_colwidth',None)
    return df

def query_skill_parameters_in(skill_uri):
    ont_iri,class_prefix,op_prefix,_,_,g = reload_graph()
    #skill_in = "TestSkill5"
    query = f""" 
        PREFIX cl: <{class_prefix}>
        PREFIX op: <{op_prefix}>
        PREFIX ont: <{ont_iri}>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT DISTINCT ?property ?ParamIndiv ?dataProp ?datavalue WHERE {{
        # Startpunkt der Kette
        <{skill_uri}> a cl:Skill;
            ?property ?ParamIndiv .
        ?property rdfs:subPropertyOf op:offersSkillParameter.
        FILTER regex(str(?property), "ParameterIn")
        ?ParamIndiv ?dataProp ?datavalue.
        ?dataProp a owl:DatatypeProperty.
        }}
        """


    relation_results = g.query(query)
    df = pd.DataFrame(relation_results, columns=[str(var) for var in relation_results.vars])
    return df

def query_skill_parameters_without_pos(skill_uri):
    ont_iri, class_prefix, op_prefix, _, _, g = reload_graph()
    
    query = f""" 
    PREFIX cl: <{class_prefix}>
    PREFIX op: <{op_prefix}>
    PREFIX ont: <{ont_iri}>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT DISTINCT ?property ?ParamIndiv ?dataProp ?datavalue WHERE {{
        <{skill_uri}> a cl:Skill ;
            ?property ?ParamIndiv .
        ?property rdfs:subPropertyOf op:offersSkillParameter .
        ?ParamIndiv ?dataProp ?datavalue .
        ?dataProp a owl:DatatypeProperty .
        FILTER ( !regex(str(?property), "Position") )
    }}
    """
    
    result = g.query(query)
    df = pd.DataFrame(result, columns=[str(var) for var in result.vars])
    return df
#df1 = query_skill_parameters_out("http://www.semanticweb.org/SkillOA/2025/3/KBI/Skill_MoveConveyorBeltWithA01")
#df2 = query_skill_parameters_in("http://www.semanticweb.org/SkillOA/2025/3/KBI/Skill_MoveConveyorBeltForwardWithA01")
#print(df1)
#print(df2)
#return df
    #print(res)
#for index,row in df.iterrows():
    #property_uri = str(row['property'])
    #check_prop_uri = property_uri.replace("ParameterOut", "ParameterIn")
    #dataprop_uri = str(row['dataProp'])
    #datavalue = str(row['datavalue'])
    #print(check_prop_uri)
    #tr=check_skill_match_num_range(skill_in,property_uri,dataprop_uri,datavalue)
    #print(tr)
    #
            #skill_uri = str(row['skill'])
            #if nextGlied.startswith(str(ont_iri)):
    #print(property_uri)
            #print(nextGlied_uri)
def get_position_string(skill_uri, param_type="out"):
    """
    Holt den PositionRange-Wert als string z.B. "[1;1;1]" oder "[1;1;1];[2;2;2]"
    """
    df = query_skill_parameters_out(skill_uri) if param_type == "out" else query_skill_parameters_in(skill_uri)
    try:
        return df[df['dataProp'].str.contains("PositionRange")]['datavalue'].iloc[0]
    except:
        return None

def position_strings_match(pos_out_str, pos_in_str):
    """
    Verwendet Nutzerin-Funktion zur Prüfung, ob PositionOut zur PositionIn passt
    """
    try:
        if pos_out_str is None:
            return True  # Kein Ausgang heißt alles als Folgeglied erlaubt
        if pos_in_str is None:
            return True  # Kein Eingang heißt alles als Vorangegangenes Glied erlaubt
        e1 = pos_out_str.count("[")
        e2 = pos_out_str.count("]")
        if e1 == 1 and e2 == 1:
            return is_position_in_range(pos_in_str, pos_out_str)
        elif e1 > 1 and e2 > 1 and e1 == e2:
            return ranges_overlap(pos_in_str, pos_out_str)
        else:
            print("Ungültiger Positionswert:", pos_out_str)
            return False
    except Exception as e:
        print(f"Fehler bei Positionsvergleich: {e}")
        return False
    
def get_next_skills(skill_uri):
    _, _, op_prefix, _, _, g = reload_graph()
    query = f"""
    PREFIX op: <{op_prefix}>
    SELECT ?next WHERE {{
        <{skill_uri}> op:hasNextSkill ?next .
    }}
    """
    results = g.query(query)
    return [str(row.next) for row in results]

def skill_transition_allowed(skill_out, skill_in):
    """
    Prüft, ob der Übergang von skill_out zu skill_in erlaubt ist.
    Kapselt Positions-, Material-, Farbvergleich usw. 

    Hier kann man alle zusätzlichen Restriktionen einbauen, die man will.
    """
    #Position prüfen
    pos_out_str = get_position_string(skill_out, "out")
    pos_in_str = get_position_string(skill_in, "in")

    if not position_strings_match(pos_out_str, pos_in_str):
        return False

    # Beispiel für weitere Checks (noch zu implementieren):
    # if not material_match(skill_out, skill_in):
    #     return False
    # if not color_match(skill_out, skill_in):
    #     return False

    return True
from collections import Counter

def find_valid_skill_paths(current_skill, path_so_far, all_paths,
                           last_skill=None, last_skill_count=0,
                           same_start_and_end=False, skill_visit_counts=None,
                           required_parameters=None):
    if skill_visit_counts is None:
        skill_visit_counts = Counter()

    # Aktuellen Skill-Zähler erhöhen
    skill_visit_counts[current_skill] += 1

    # Maximal 2 Ausführungen erlaubt
    if skill_visit_counts[current_skill] > 2:
        return

    # Zusätzliche Logik: Abbruch, wenn Skill nicht erlaubten Output erzeugt
    if required_parameters is not None:
        output_df = query_skill_parameters_without_pos(current_skill)
        for _, row in output_df.iterrows():
            param = (str(row["dataProp"]), str(row["datavalue"]))
            if param not in required_parameters:
                print(f"Skill {current_skill} erzeugt nicht erlaubten Output: {param}")
                return

    # Prüfen, ob Ziel-Skill erreicht wurde
    if current_skill == last_skill:
        last_skill_count += 1
        if (same_start_and_end and last_skill_count >= 2) or \
           (not same_start_and_end and last_skill_count >= 1):
            all_paths.append(path_so_far)
            return

    next_skills = get_next_skills(current_skill)
    found_valid = False

    for next_skill in next_skills:
        if skill_transition_allowed(current_skill, next_skill):
            find_valid_skill_paths(
                next_skill,
                path_so_far + [next_skill],
                all_paths,
                last_skill,
                last_skill_count,
                same_start_and_end,
                skill_visit_counts.copy(),
                required_parameters  # Weiterreichen
            )
            found_valid = True

    # Wenn kein gültiger Übergang mehr möglich war, optional Pfad speichern
    if not found_valid:
        if (same_start_and_end or last_skill is None) or last_skill_count < 2:
            all_paths.append(path_so_far)

"""

def find_valid_skill_paths(current_skill, path_so_far, all_paths,
                           last_skill=None, last_skill_count=0,
                           same_start_and_end=False, skill_visit_counts=None):
    if skill_visit_counts is None:
        skill_visit_counts = Counter()

    # Aktuellen Skill-Zähler erhöhen
    skill_visit_counts[current_skill] += 1

    # Maximal 2 Ausführungen erlaubt
    if skill_visit_counts[current_skill] > 2:
        return

    # Prüfen, ob Ziel-Skill erreicht wurde
    if current_skill == last_skill:
        last_skill_count += 1
        if (same_start_and_end and last_skill_count >= 2) or \
           (not same_start_and_end and last_skill_count >= 1):
            all_paths.append(path_so_far)
            return

    next_skills = get_next_skills(current_skill)
    found_valid = False

    for next_skill in next_skills:
        if skill_transition_allowed(current_skill, next_skill):
            # Rekursiv weitersuchen mit Kopie der Zählung
            find_valid_skill_paths(
                next_skill,
                path_so_far + [next_skill],
                all_paths,
                last_skill,
                last_skill_count,
                same_start_and_end,
                skill_visit_counts.copy()
            )
            found_valid = True

    # Wenn kein gültiger Übergang mehr möglich war, optional Pfad speichern
    if not found_valid:
        if (same_start_and_end or last_skill is None) or last_skill_count < 2:
            all_paths.append(path_so_far)
"""
            
"""
def get_all_valid_skill_paths_forward(start_skill, last_skill=None):
    all_paths = []

    same_start_and_end = start_skill == last_skill and last_skill is not None

    find_valid_skill_paths(
        current_skill=start_skill,
        path_so_far=[start_skill],
        all_paths=all_paths,
        last_skill=last_skill,
        last_skill_count=0,
        same_start_and_end=same_start_and_end
    )
    
    return all_paths
"""

## Rückwärtssuche nötig, damit von jedem Punkt aus gegangen werden kann, sonst Umgehen von Alternativverzweigungen.
####################################################################################################################################################
def get_previous_skills(skill_uri):
    _, _, op_prefix, _, _, g = reload_graph()
    query = f"""
    PREFIX op: <{op_prefix}>
    SELECT ?prev WHERE {{
        ?prev op:hasNextSkill <{skill_uri}> .
    }}
    """
    results = g.query(query)
    return [str(row.prev) for row in results]

def find_valid_skill_paths_backward(current_skill, path_so_far, all_paths,
                                    first_skill=None, first_skill_count=0,
                                    same_start_and_end=False, skill_visit_counts=None,
                                    required_parameters=None):  # NEU
    if skill_visit_counts is None:
        skill_visit_counts = {}

    skill_visit_counts[current_skill] = skill_visit_counts.get(current_skill, 0) + 1

    if skill_visit_counts[current_skill] > 2:
        return

    # Zusatz: prüfe, ob aktueller Skill unzulässige Outputs hat
    df_out = query_skill_parameters_without_pos(current_skill)
    for _, row in df_out.iterrows():
        prop = str(row["dataProp"])
        val = str(row["datavalue"])
        if (prop, val) not in required_parameters:
            print(f"Skill {current_skill} erzeugt nicht erlaubten Output: ({prop}, {val})")
            return  # Rückwärtsabbruch

    if current_skill == first_skill:
        first_skill_count += 1
        if (same_start_and_end and first_skill_count >= 2) or (not same_start_and_end and first_skill_count >= 1):
            all_paths.append(path_so_far)
            return

    previous_skills = get_previous_skills(current_skill)
    found_valid = False

    for prev_skill in previous_skills:
        if skill_transition_allowed(prev_skill, current_skill):
            find_valid_skill_paths_backward(
                prev_skill,
                [prev_skill] + path_so_far,
                all_paths,
                first_skill,
                first_skill_count,
                same_start_and_end,
                skill_visit_counts.copy(),
                required_parameters  # NEU
            )
            found_valid = True

    if not found_valid:
        if (same_start_and_end or first_skill is None) or first_skill_count < 2:
            all_paths.append(path_so_far)

def get_all_valid_skill_paths_backward(end_skill, first_skill=None, required_parameters=None):
    all_paths = []
    same_start_and_end = end_skill == first_skill and first_skill is not None

    find_valid_skill_paths_backward(
        current_skill=end_skill,
        path_so_far=[end_skill],
        all_paths=all_paths,
        first_skill=first_skill,
        first_skill_count=0,
        same_start_and_end=same_start_and_end,
        required_parameters=required_parameters  # NEU
    )
    #print("Alle backward-Pfade von", end_skill)
    #for fwd in all_paths:
        #print("  ", fwd)
    return all_paths



from collections import Counter

def find_valid_feature_fulfillment_paths(service_uri):
    lastskill = query_last_skill()
    firstskill = query_first_skill()
    parameter_df = query_service_parameters(service_uri)

    if parameter_df.empty:
        print("Keine Parameteranforderungen gefunden.")
        return []

    # Set aller erlaubten Parameter (nur diese dürfen erzeugt werden)
    required_parameters = set(
        (str(row["dataProp"]), str(row["datavalue"]))
        for _, row in parameter_df.iterrows()
    )

    # Map: (dataProp, dataValue) → passende Skills
    requirement_skills = {}
    all_matching_skills = set()

    for _, row in parameter_df.iterrows():
        dp_uri = str(row["dataProp"])
        dp_value = str(row["datavalue"])
        dfskills = find_skill_for_service_request_param(dp_uri, dp_value)

        if not dfskills.empty:
            skills = dfskills['skill'].astype(str).unique().tolist()
            requirement_skills[(dp_uri, dp_value)] = skills
            all_matching_skills.update(skills)

    all_paths = []

    for start_skill_uri_ref in all_matching_skills:
        start_skill = str(start_skill_uri_ref)
        backward_paths = get_all_valid_skill_paths_backward(
            start_skill, 
            first_skill=firstskill, 
            required_parameters=required_parameters
        )
        
        for backward in backward_paths:
            skill_counter = Counter(backward)
            skill_counter[start_skill] -= 1

            forward_paths = []

            # Hier Übergabe von required_parameters
            find_valid_skill_paths(
                current_skill=start_skill,
                path_so_far=[start_skill],
                all_paths=forward_paths,
                last_skill=lastskill,
                last_skill_count=0,
                same_start_and_end=start_skill == lastskill,
                skill_visit_counts=skill_counter.copy(),
                required_parameters=required_parameters  # ← NEU
            )

            for forward in forward_paths:
                combined_path = backward + forward[1:]  # Start-Skill nur einmal
                combined_path_strs = [str(s) for s in combined_path]

                fulfilled = set()
                start_skill_str = str(start_skill)

                for (dp_uri, dp_value), possible_skills in requirement_skills.items():
                    possible_skills_str = [str(s) for s in possible_skills]

                    if start_skill_str in possible_skills_str and start_skill_str in combined_path_strs:
                        fulfilled.add((dp_uri, dp_value))

                    for skill_str in possible_skills_str:
                        if skill_str in combined_path_strs:
                            fulfilled.add((dp_uri, dp_value))
                            #print("======== Prüfung Pfad ========")
                            #print("StartSkill: ", start_skill_str)
                            #print("Pfad:", combined_path_strs)
                            #print("Benötigte Parameter:", set(requirement_skills.keys()))
                            #print("Aktuell erfüllte:", fulfilled)
                            #print("Fehlende:", set(requirement_skills.keys()) - fulfilled)
                            break

                if set(requirement_skills.keys()).issubset(fulfilled):
                    all_paths.append(combined_path)
                    #print("Gültiger Pfad gefunden:")
                    #print(" StartSkill:", start_skill)
                    #print(" Pfad:", combined_path_strs)

    unique_paths = list({tuple(p): p for p in all_paths}.values())
    return unique_paths


import json
from rdflib import Literal
from rdflib import XSD

def add_capability_to_graph(capability_json, service_uri, nr):
    ont_iri, class_prefix, op_prefix, dp_prefix, ont_path, g = reload_graph()
    
    CL = Namespace(class_prefix)
    OP = Namespace(op_prefix)
    DP = Namespace(dp_prefix)
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    capability_id = ont_iri+"ProposedCapability" + str(nr) + "ToFulfill" + service_uri.removeprefix(str(ont_iri))
    capability_uri = URIRef(capability_id)
    
    g.add((capability_uri, RDF.type, CL.ProposedCapability))
    g.add((capability_uri, OP.canFulfill, URIRef(service_uri)))

    # JSON-String → Python-Objekt (Liste mit Skill-Dictionaries)
    capability_data = json.loads(capability_json)

    for skill_obj in capability_data:
        skill_uri = URIRef(skill_obj["skill"])
        g.add((capability_uri, OP.hasSkill, skill_uri))
    
    # Skillmodell als JSON-String speichern
    g.add((capability_uri, DP.hasSkillModel, Literal(capability_json, datatype=XSD.string)))
    g.serialize(destination=ont_path, format="turtle")

        
        # Optional: Position in Capability speichern
        #pos = skill_obj.get("position_in_Capability")
        #if pos is not None:
        #    position_dp = URIRef(f"{ont_iri}dp_hasPositionInCapability")
        #    g.add((skill_uri, position_dp, Literal(pos)))


service_uri = "http://www.semanticweb.org/SkillOA/2025/3/KBI/TestServiceRequest2"
valid_paths = find_valid_feature_fulfillment_paths(service_uri)



for i, path in enumerate(valid_paths):
    print(f"\nPfad {i+1}:")
    capability_json_entries = []
    for j, skill in enumerate(path):
        print(f"  --> {skill}")

        # JSON-Infos pro Skill abfragen (sollte Liste mit 1 Objekt sein!)
        json_str = query_skill_all_skill_information(skill)
        skill_info = json.loads(json_str)[0]  # Nur ein Objekt pro Skill

        # Position oben setzen (nicht in "parameters", sondern ganz oben)
        skill_info["position_in_Capability"] = j + 1

        # JSON-Objekt zur Capability-Liste hinzufügen
        capability_json_entries.append(skill_info)

    capability_json = json.dumps(capability_json_entries, indent=2)
    add_capability_to_graph(capability_json, service_uri, i + 1)
    #print(i+1)
    #print(capability_json)

# Am Ende alle Einträge gesammelt als JSON ausgeben
#final_json = json.dumps(capability_json_entries, indent=2)
#print("\n⚙️ Capability JSON:")
#print(final_json)