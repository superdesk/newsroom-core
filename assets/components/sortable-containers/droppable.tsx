/* eslint-disable react/prop-types */
import React from 'react';
import {useDroppable} from '@dnd-kit/core';

interface IProps {
    containerId: string;
}

export const Droppable: React.ComponentType<IProps> = (props) => {
    // This is needed for empty column to be droppable
    const {setNodeRef} = useDroppable({
        id: props.containerId,
    });

    return (
        <div
            ref={setNodeRef}
        >
            {props.children}
        </div>
    );
};
