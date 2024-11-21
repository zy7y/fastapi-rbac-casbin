from typing import Any


def list2tree(
    arr: list[dict[str, Any]], parent_name="parent_id", children_name="children"
) -> list[dict[str, Any]]:
    """
    List 转 Tree
    :param arr:
    :param parent_name:
    :param children_name:
    :return:
    """
    menu_map = {item["id"]: item for item in arr}
    menu_tree = []

    for item in arr:
        if item.get(parent_name) is None:
            menu_tree.append(item)
        else:
            parent_item = menu_map.get(item[parent_name])
            if parent_item is not None:
                parent_item.setdefault(children_name, []).append(item)

    return menu_tree
