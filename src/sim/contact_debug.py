import pybullet as pyb


def print_contacts_for_body(body_id, label):
    contacts = pyb.getContactPoints(bodyA=body_id)

    if not contacts:
        print(f"{label}: no contacts")
        return

    print(f"{label}: {len(contacts)} contact(s)")
    for contact in contacts:
        body_a = contact[1]
        body_b = contact[2]
        link_a = contact[3]
        link_b = contact[4]
        force = contact[9]
        print(
            f"  body {body_a} link {link_a} <-> "
            f"body {body_b} link {link_b}, force={force:.3f}"
        )
