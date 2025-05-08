# Laden ont
from rdflib import Graph
from pathlib import Path
from rdflib import Graph, URIRef, RDF, Namespace, OWL, RDFS
from rdflib.namespace import XSD
import pandas as pd
import os
from collections import namedtuple
# Initialisierung
OntologyData = namedtuple("OntologyData", [
    "ont_iri", "class_pr","op_pr","dp_pr","ont_path","g"
])

def reload_graph():
    ont_iri = "http://www.w3id.org/hsu-aut/css#"
    ont_ir = Namespace(ont_iri)
    class_pr = Namespace(f"{ont_iri}class_")
    op_pr = Namespace(f"{ont_iri}op_")
    dp_pr = Namespace(f"{ont_iri}dp_")

    ontology_path = Path(r"C:\Users\Alexander Verkhov\Downloads\Paper Ontologies\CSS.ttl")
    
    if not ontology_path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {ontology_path}")

    g = Graph()

    # Statt file=..., den Inhalt als String lesen
    ttl_text = ontology_path.read_text(encoding="utf-8")
    g.parse(data=ttl_text, format="turtle")

    return OntologyData(ont_ir, class_pr, op_pr, dp_pr, ontology_path, g)
#reload_graph()
data = reload_graph()
print(data.ont_iri)

#Berechning CI

def get_all_classes(graph):
    return set(graph.subjects(RDF.type, OWL.Class))

def get_all_instances(graph):
    return set(graph.subjects(RDF.type, OWL.NamedIndividual))

def get_instances_of_class(graph, class_uri):
    return set(graph.subjects(RDF.type, URIRef(class_uri)))

def get_all_subclasses(graph, super_class):
    subclasses = {(super_class, 0)}  # Klasse selbst mit Tiefe 0
    to_visit = [(super_class, 0)]
    
    while to_visit:
        current, depth = to_visit.pop()
        for subclass in graph.subjects(RDFS.subClassOf, URIRef(current)):
            if (subclass, depth + 1) not in subclasses:
                subclasses.add((subclass, depth + 1))
                to_visit.append((subclass, depth + 1))
    
    return subclasses  # Set of (subclass_uri, depth)


def calculate_ci_for_class(graph, class_uri, total_instances):
    ci_value = 0.0
    subclasses = get_all_subclasses(graph, class_uri)

    for subclass_uri, depth in subclasses:
        instances = get_instances_of_class(graph, subclass_uri)
        if instances:
            print(f"{subclass_uri} mit {len(instances)} Instanzen auf Tiefe {depth}")
        ir = len(instances) / total_instances if total_instances > 0 else 0
        ci_value += ir / (2 ** depth)

    return ci_value

def calculate_ci_all_classes(graph):
    all_classes = get_all_classes(graph)
    all_instances = get_all_instances(graph)
    total_instances = len(all_instances)

    ci_results = {}

    for class_uri in all_classes:
        ci = calculate_ci_for_class(graph, class_uri, total_instances)
        ci_results[str(class_uri)] = ci

    return ci_results, total_instances


ci_per_class, total_instances = calculate_ci_all_classes(data.g)

for class_uri, ci in ci_per_class.items():
    print(f"CI({class_uri}) = {ci:.5f}")

average_ci = sum(ci_per_class.values()) / len(ci_per_class) if ci_per_class else 0
print(f"Durchschnittliches CI über alle Klassen: {average_ci:.5f}")

#Berechnung SPA

def get_all_classes(graph):
    return set(graph.subjects(RDF.type, OWL.Class))

def get_properties_with_domains(graph):
    return set(graph.subjects(RDFS.domain, None))

def get_domain_of_property(graph, prop):
    return set(graph.objects(prop, RDFS.domain))

def get_superclasses(graph, cls):
    superclasses = set()
    to_visit = [cls]
    while to_visit:
        current = to_visit.pop()
        for super_cls in graph.objects(current, RDFS.subClassOf):
            if super_cls not in superclasses:
                superclasses.add(super_cls)
                to_visit.append(super_cls)
    return superclasses

def is_property_unique_to_subclass(graph, prop, subclass):
    domains = get_domain_of_property(graph, prop)
    for domain in domains:
        if domain == subclass:
            superclasses = get_superclasses(graph, subclass)
            for sup in superclasses:
                if (prop, RDFS.domain, sup) in graph:
                    return False
            return True
    return False

def calculate_spa_local(graph):
    classes = get_all_classes(graph)
    props = get_properties_with_domains(graph)

    unique_properties = set()

    for prop in props:
        for cls in classes:
            if is_property_unique_to_subclass(graph, prop, cls):
                unique_properties.add(prop)

    total_unique_properties = len(unique_properties)
    total_classes = len(classes)

    if total_classes == 0:
        return 0.0

    return total_unique_properties / total_classes

spa_value = calculate_spa_local(data.g)
print(f"SPA-Value: {spa_value:.2f}")

#SPI

def get_all_classes_with_superclasses(graph):
    result = []
    for cls in graph.subjects(RDF.type, OWL.Class):
        for superclass in graph.objects(cls, RDFS.subClassOf):
            result.append((cls, superclass))
    return result

def get_instances_of_class(graph, class_uri):
    return set(graph.subjects(RDF.type, URIRef(class_uri)))

def get_instance_properties(graph, instance_uris):
    props = set()
    for inst in instance_uris:
        for pred in graph.predicates(subject=inst):
            if pred != RDF.type:
                props.add(pred)
    return props

def calculate_spi_for_class(graph, class_uri, superclass_uri):
    class_instances = get_instances_of_class(graph, class_uri)
    superclass_instances = get_instances_of_class(graph, superclass_uri)

    class_props = get_instance_properties(graph, class_instances)
    superclass_props = get_instance_properties(graph, superclass_instances)

    total_count = len(class_props)
    specific_count = len(class_props - superclass_props)

    if total_count == 0:
        return 0.0

    return specific_count / total_count

def calculate_average_spi_local(graph):
    spi_values = []
    class_pairs = get_all_classes_with_superclasses(graph)

    print("SPI-Werte je Klasse:\n")

    for class_uri, superclass_uri in class_pairs:
        spi = calculate_spi_for_class(graph, class_uri, superclass_uri)
        spi_values.append(spi)
        print(f"Klasse: {class_uri}")
        print(f"->Oberklasse: {superclass_uri}")
        print(f"  SPI: {spi:.5f}\n")

    if not spi_values:
        return 0.0

    return sum(spi_values) / len(spi_values)


average_spi = calculate_average_spi_local(data.g)
print(f"Durchschnittlicher SPI: {average_spi:.10f}")


#Berechnung ICR

def get_all_classes(graph):
    return set(graph.subjects(RDF.type, OWL.Class))

def get_classes_with_instances(graph):
    classes_with_instances = set()
    for instance in graph.subjects(RDF.type, OWL.NamedIndividual):
        for cls in graph.objects(instance, RDF.type):
            classes_with_instances.add(cls)
    return classes_with_instances

def calculate_icr(graph):
    all_classes = get_all_classes(graph)
    used_classes = get_classes_with_instances(graph)

    if not all_classes:
        return 0.0

    return len(used_classes & all_classes) / len(all_classes)

icr_value = calculate_icr(data.g)

#IPR
from rdflib import Graph, RDF, RDFS, OWL

def get_all_defined_properties(graph):
    props = set()
    for p in graph.subjects(RDF.type, RDF.Property):
        props.add(p)
    for p in graph.subjects(RDF.type, OWL.ObjectProperty):
        props.add(p)
    for p in graph.subjects(RDF.type, OWL.DatatypeProperty):
        props.add(p)
    return props

def get_all_used_properties(graph):
    used_props = set()
    for s, p, o in graph:
        if p != RDF.type:  # rdf:type ausschließen
            used_props.add(p)
    return used_props

def calculate_ipr(graph):
    defined_props = get_all_defined_properties(graph)
    used_props = get_all_used_properties(graph)

    if not defined_props:
        return 0.0

    return len(used_props & defined_props) / len(defined_props)



ipr_value = calculate_ipr(data.g)

print(f"Definierte Properties (N(P)): {len(get_all_defined_properties(data.g))}")
print(f"Verwendete Properties (N(IP)): {len(get_all_used_properties(data.g))}")
print(f"Instantiated Property Ratio (IPR): {ipr_value:.4f}")

print(f"Anzahl der Klassen: {len(get_all_classes(data.g))}")
print(f"Klassen mit mindestens einer Instanz: {len(get_classes_with_instances(data.g))}")
print(f"ICR-Wert: {icr_value:.5f}")

#IMI berechnen

def calculate_imi_local(graph):
    classes = set(graph.subjects(RDF.type, OWL.Class))
    total_superclasses = 0
    class_count = 0

    for cls in classes:
        superclasses = set(graph.objects(cls, RDFS.subClassOf))
        # owl:Thing ausschließen
        filtered_superclasses = {sc for sc in superclasses if str(sc) != str(OWL.Thing)}
        nsup = len(filtered_superclasses)

        print(f"Klasse: {cls}, Anzahl direkter Oberklassen: {nsup}")
        total_superclasses += nsup
        class_count += 1

    if class_count == 0:
        return 0.0

    average_superclass_count = total_superclasses / class_count
    imi = 1 / average_superclass_count if average_superclass_count > 0 else 0.0

    print(f"Anzahl Klassen (Nc): {class_count}")
    print(f"Summe direkter Oberklassen: {total_superclasses}")
    print(f"Durchschnittliche Anzahl Oberklassen: {average_superclass_count:.4f}")
    print(f"IMI-Wert: {imi:.4f}")

    return imi
imi_value = calculate_imi_local(data.g)