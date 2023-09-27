import React from 'react';
import {useDraggable} from '@dnd-kit/core';
import {CSS} from '@dnd-kit/utilities';

interface IProps {
    id: string;
    children: React.ReactNode;
}

/**
 * Having it as a separate component helps to avoid re-rendering of children while dragging
 */
export function Draggable(props: IProps) {
    const {attributes, listeners, setNodeRef, transform} = useDraggable({
        id: props.id,
    });

    const style = {
        transform: CSS.Translate.toString(transform),
    };

    return (
        <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
            {props.children}
        </div>
    );
}
