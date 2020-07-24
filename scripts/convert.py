import json
import yaml

schemav1 = "schema/dandiset.json"

mapping = {'identifier': ['identifier'],
           'name': ['name'],
           'description': ['description'],
           'contributors': ['contributor'],
           'sponsors': ['contributor', ['Sponsor']],
           'license': ['license'],
           'keywords': ['keywords'],
           'project': ['generatedBy'],
           'conditions_studied': ['about'],
           'associated_anatomy': ['about'],
           'protocols': ['protocol'],
           'ethicsApprovals': ['ethicsApproval'],
           'access': ['access'],
           'associatedData': ['relatedResource', 'IsDerivedFrom'],
           'publications': ['relatedResource', 'IsDescribedBy'],
           'age': ['variableMeasured'],
           'organism': ['variableMeasured'],
           'sex': ['variableMeasured'],
           'number_of_subjects': ['assetsSummary', 'numberOfSubjects'],
           'number_of_cells': ['assetsSummary', 'numberOfCells'],
           'number_of_tissue_samples': ['assetsSummary', 'numberOfSamples'],
           }


def toContributor(value):
    if not isinstance(value, list):
        value = [value]
    out = []
    for item in value:
        contrib = {}
        name = item["name"].split()
        item["name"] = f"{name[-1]}, {' '.join(name[:-1])}"
        if "roles" in item:
            roles = []
            for role in item["roles"]:
                tmp = role.split()
                if len(tmp) > 1:
                    roles.append("".join([val.capitalize() for val in tmp]))
                else:
                    roles.append(tmp.pop())
            contrib["roleName"] = roles
            del item["roles"]
        if "awardNumber" in item:
            contrib["awardNumber"] = item["awardNumber"]
            del item["awardNumber"]
        if "orcid" in item:
            if item["orcid"]:
                contrib["identifier"] = {"value": item["orcid"],
                                         "propertyID": "ORCID"}
            else:
                contrib["identifier"] = ""
            del item["orcid"]
        if "affiliations" in item:
            item["affiliation"] = item["affiliations"]
            del item["affiliations"]
        contrib.update(**{f"{k}":v for k,v in item.items()})
        out.append(contrib)
    return out


def convertv1(filename):
    with open(filename) as fp:
        data = json.load(fp)
    oldmeta = data["dandiset"] if "dandiset" in data else data
    newmeta = {}
    for oldkey, value in oldmeta.items():
        if oldkey in ['language', 'altid', 'number_of_slices']:
            continue
        if oldkey not in mapping:
            raise KeyError(f"Could not find {oldkey}")
        if len(mapping[oldkey]) == 0:
            newkey = f"schema:{oldkey}"
        else:
            newkey = mapping[oldkey][0]
        if oldkey in ['contributors', "sponsors"]:
            value = toContributor(value)
        if oldkey == "access":
            value = [{"email": value["access_contact_email"],
                      "status": value["status"].capitalize()}]
        if oldkey == "identifier":
            value = {"value": value,
                     "propertyID": "DANDI"}
        if len(mapping[oldkey]) == 2:
            extra = mapping[oldkey][1]
            if newkey == 'contributor':
                extrakey = 'roleName'
            if oldkey == 'sponsors':
                extrakey = 'roleName'
            if oldkey in ['publications', 'associatedData']:
                extrakey = 'relation'
                if not isinstance(value, list):
                    value = [value]
                out = []
                for item in value:
                    if isinstance(item, dict):
                        out.append({k:v for k,v in item.items()})
                    else:
                        present = False
                        for val in out:
                            if item in val.values():
                                present = True
                        if not present:
                            out.append({"url": item})
                value = out
            if oldkey in ['number_of_subjects', 'number_of_cells',
                          'number_of_tissue_samples']:
                value = {extra: value}
                extrakey = None
            if isinstance(value, list):
                for val in value:
                    if extrakey:
                        val[extrakey] = extra
            if isinstance(value, dict):
                if extrakey:
                    value[extrakey] = extra
        if newkey == 'variableMeasured':
            if oldkey in ["age", "sex"]:
                vm = {"name": oldkey}
                if oldkey == "sex":
                    vm["value"] = value
                else:
                    if "maximum" in value:
                        if "days" in value["maximum"]:
                            value["units"] = "days"
                        if "Gestational" in value["maximum"]:
                            value["units"] = "Gestational Week"
                            value["maximum"] = value["maximum"].split()[-1]
                        if value["maximum"].startswith("P"):
                            value["maximum"] = value["maximum"][1:-1]
                            value["units"] = value["maximum"][-1]
                        if "None" not in value["maximum"]:
                            value["maximum"] = float(value["maximum"].split()[0])
                    if "minimum" in value:
                        if "days" in value["minimum"]:
                            value["units"] = "days"
                        if "Gestational" in value["minimum"]:
                            value["units"] = "Gestational Week"
                            value["minimum"] = value["minimum"].split()[-1]
                        if value["minimum"].startswith("P"):
                            value["minimum"] = value["minimum"][1:-1]
                            value["units"] = value["minimum"][-1]
                        if "None" not in value["minimum"]:
                            value["minimum"] = float(value["minimum"].split()[0])
                    value["unitText"] = value["units"]
                    del value["units"]
                    vm.update(**value)
            else:
                newvalues = []
                for val in value:
                    if "species" in val:
                        newvalues.append(val["species"])
                vm = {"name": "species", "value": newvalues}
            value = vm
        if newkey not in newmeta:
            newmeta[newkey] = value
        else:
            curvalue = newmeta[newkey]
            if not isinstance(curvalue, list):
                newmeta[newkey] = [curvalue]
            if not isinstance(value, list):
                value = [value]
            newmeta[newkey].extend(value)
    if "assetsSummary" in newmeta:
        del newmeta["assetsSummary"]
    if "variableMeasured" in newmeta:
        del newmeta["variableMeasured"]
    return newmeta


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = "scripts/dandiset_000004.json"
    newmeta = convertv1(filename)

    # validate via the model
    from models import PublishedDandiset
    dandiset = PublishedDandiset.unvalidated(**newmeta)
    with open(filename.replace(".json", "_converted.yaml"), "wt") as fp:
        yaml.dump(dict(dandiset), fp, indent=2)

    data = PublishedDandiset(**newmeta)
