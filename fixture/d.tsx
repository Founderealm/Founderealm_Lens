import React from "react";
interface Props { id: string }
export function Widget(props: Props) { return React.createElement("div", null, props.id); }
