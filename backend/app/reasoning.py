from collections import Counter
from typing import List

from .schemas import Detection


# ---------------------------------------------------------
# INTENT DETECTION
# ---------------------------------------------------------

def detect_intent(query: str) -> str:

    q = query.lower().strip()

    if any(word in q for word in [
        "how many",
        "count",
        "number of"
    ]):
        return "COUNT"

    if any(word in q for word in [
        "helmet",
        "hardhat",
        "head protection"
    ]):
        return "HELMET"

    if any(word in q for word in [
        "vest",
        "visibility",
        "safety vest"
    ]):
        return "VEST"

    if any(word in q for word in [
        "goggle",
        "goggles",
        "eye protection"
    ]):
        return "GOGGLE"

    if any(word in q for word in [
        "glove",
        "gloves",
        "hand protection"
    ]):
        return "GLOVE"

    if any(word in q for word in [
        "boot",
        "boots",
        "foot protection"
    ]):
        return "BOOT"

    if any(word in q for word in [
        "safe",
        "safety",
        "compliance",
        "compliant",
        "violation",
        "ppe"
    ]):
        return "SAFETY"

    return "GENERAL"


# ---------------------------------------------------------
# COUNT DETECTIONS
# ---------------------------------------------------------

def get_counts(
    detections: List[Detection]
):

    return Counter(
        detection.class_name.lower()
        for detection in detections
    )


# ---------------------------------------------------------
# CONFIDENCE ANALYSIS
# ---------------------------------------------------------

def confidence_level(
    detections: List[Detection]
) -> str:

    if not detections:
        return "LOW"

    average = sum(
        d.confidence for d in detections
    ) / len(detections)

    if average >= 0.80:
        return "HIGH"

    if average >= 0.60:
        return "MEDIUM"

    return "LOW"


# ---------------------------------------------------------
# SAFETY ANALYSIS
# ---------------------------------------------------------

def safety_analysis(
    detections: List[Detection]
):

    counts = get_counts(detections)

    persons = counts.get("person", 0)

    helmets = counts.get("helmet", 0)
    no_helmets = counts.get("no_helmet", 0)

    vests = counts.get("vest", 0)
    no_vests = counts.get("no-safety vest", 0)

    goggles = counts.get("goggles", 0)
    no_goggles = counts.get("no_goggle", 0)

    gloves = counts.get("gloves", 0)
    no_gloves = counts.get("no_gloves", 0)

    boots = counts.get("boots", 0)
    no_boots = counts.get("no_boots", 0)

    violations = []

    if no_helmets > 0:
        violations.append(
            f"{no_helmets} possible worker(s) without helmet"
        )

    if no_vests > 0:
        violations.append(
            f"{no_vests} possible worker(s) without safety vest"
        )

    if no_goggles > 0:
        violations.append(
            f"{no_goggles} possible worker(s) without goggles"
        )

    if no_gloves > 0:
        violations.append(
            f"{no_gloves} possible worker(s) without gloves"
        )

    if no_boots > 0:
        violations.append(
            f"{no_boots} possible worker(s) without boots"
        )

    # -----------------------------------------------------
    # Decision logic
    # -----------------------------------------------------

    if persons == 0:
        status = "INSUFFICIENT_INFORMATION"

    elif violations:
        status = "ATTENTION_REQUIRED"

    else:
        status = "NO_DETECTED_VIOLATIONS"

    return {
        "status": status,
        "persons": persons,
        "helmets": helmets,
        "no_helmets": no_helmets,
        "vests": vests,
        "no_vests": no_vests,
        "goggles": goggles,
        "no_goggles": no_goggles,
        "gloves": gloves,
        "no_gloves": no_gloves,
        "boots": boots,
        "no_boots": no_boots,
        "violations": violations
    }


# ---------------------------------------------------------
# QUERY REASONING
# ---------------------------------------------------------

def answer_query(
    query: str,
    detections: List[Detection]
):

    intent = detect_intent(query)
    counts = get_counts(detections)

    confidence = confidence_level(detections)

    # -----------------------------------------------------
    # COUNT
    # -----------------------------------------------------

    if intent == "COUNT":

        q = query.lower()

        if "person" in q or "worker" in q:

            count = counts.get("person", 0)

            return (
                intent,
                f"{count} person(s) detected.",
                "INFORMATION"
            )

        if "helmet" in q:

            count = counts.get("helmet", 0)

            return (
                intent,
                f"{count} helmet(s) detected.",
                "INFORMATION"
            )

        if "vest" in q:

            count = counts.get("vest", 0)

            return (
                intent,
                f"{count} safety vest(s) detected.",
                "INFORMATION"
            )

        if "goggle" in q:

            count = counts.get("goggles", 0)

            return (
                intent,
                f"{count} pair(s) of goggles detected.",
                "INFORMATION"
            )

        return (
            intent,
            "I can count detected workers, helmets, vests, goggles, gloves and boots.",
            "INFORMATION"
        )

    # -----------------------------------------------------
    # HELMET
    # -----------------------------------------------------

    if intent == "HELMET":

        helmet_count = counts.get("helmet", 0)
        violation_count = counts.get("no_helmet", 0)

        if violation_count > 0:

            return (
                intent,
                f"Detected {violation_count} possible worker(s) without a helmet.",
                "ATTENTION_REQUIRED"
            )

        return (
            intent,
            f"Detected {helmet_count} helmet(s). No explicit no-helmet detection was found.",
            "NO_DETECTED_VIOLATIONS"
        )

    # -----------------------------------------------------
    # VEST
    # -----------------------------------------------------

    if intent == "VEST":

        vest_count = counts.get("vest", 0)
        violation_count = counts.get("no-safety vest", 0)

        if violation_count > 0:

            return (
                intent,
                f"Detected {violation_count} possible worker(s) without a safety vest.",
                "ATTENTION_REQUIRED"
            )

        return (
            intent,
            f"Detected {vest_count} safety vest(s). No explicit no-vest detection was found.",
            "NO_DETECTED_VIOLATIONS"
        )

    # -----------------------------------------------------
    # GENERAL SAFETY
    # -----------------------------------------------------

    if intent == "SAFETY":

        analysis = safety_analysis(detections)

        if analysis["status"] == "INSUFFICIENT_INFORMATION":

            return (
                intent,
                "Insufficient visual evidence to determine PPE compliance.",
                "INSUFFICIENT_INFORMATION"
            )

        if analysis["violations"]:

            message = (
                "Potential PPE violations detected: "
                + "; ".join(analysis["violations"])
                + "."
            )

            return (
                intent,
                message,
                "ATTENTION_REQUIRED"
            )

        return (
            intent,
            "No explicit PPE violations were detected in the image. "
            "This does not guarantee complete safety compliance.",
            "NO_DETECTED_VIOLATIONS"
        )

    # -----------------------------------------------------
    # GENERAL
    # -----------------------------------------------------

    return (
        intent,
        f"I detected {len(detections)} object(s) in the image.",
        "INFORMATION"
    )