import React from 'react';
import {DragOverlay, useDndContext} from '@dnd-kit/core';

interface IProps<T> {
    template: React.ComponentType<{itemId: string; context: T}>;
    context: T;
}

/**
 * Required to prevent item that is being dragged from visually disappearing when dragged outside sortable container
 * https://docs.dndkit.com/api-documentation/draggable/drag-overlay
 */
export function Overlay<T>(props: IProps<T>) {
    const {active} = useDndContext();

    const Template = props.template;

    return (
        <DragOverlay>
            {active ? <Template itemId={active.id.toString()} context={props.context} /> : null}
        </DragOverlay>
    );
}