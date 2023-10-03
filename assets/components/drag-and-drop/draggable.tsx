import React from 'react';
import {useDraggable} from '@dnd-kit/core';
import {CSS} from '@dnd-kit/utilities';

interface IProps {
    id: string;
    hideWhileDragging?: boolean; // avoids ghosting when scrolling with overlay enabled
    children: React.ReactNode;
}

/**
 * Having it as a separate component helps to avoid re-rendering of children while dragging
 */
export function Draggable(props: IProps) {
    const {attributes, listeners, setNodeRef, transform, isDragging} = useDraggable({
        id: props.id,
    });

    const style: React.CSSProperties = {
        transform: CSS.Translate.toString(transform),
    };

    if (props.hideWhileDragging === true && isDragging) {
        style.visibility = 'hidden';
    }

    return (
        <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
            {props.children}
        </div>
    );
}
