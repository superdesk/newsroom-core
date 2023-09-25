
import React, {useCallback} from 'react';
import {DndContext, DragOverEvent, UniqueIdentifier} from '@dnd-kit/core';
import {SortableContext, arrayMove} from '@dnd-kit/sortable';
import {SortableItem} from './sortable-item';
import {Overlay} from './overlay';

type IGroupedItems = {[key: string]: Array<string>};

interface IProps<T> {
    items: IGroupedItems;
    setItems: React.Dispatch<React.SetStateAction<IGroupedItems>>;
    containerTemplate: React.ComponentType<{containerId: string; context: T;}>;
    itemTemplate: React.ComponentType<{itemId: string; context: T;}>;
    context: T;
}

export function SortableContainers<T>(props: IProps<T>) {
    const {items, setItems} = props;

    const ContainerTemplate = props.containerTemplate;
    const ItemTemplate = props.itemTemplate;

    const findContainer = useCallback(
        (id: UniqueIdentifier) => {
            // if the id is a container id itself
            if (id in items) return id;

            // find the container by looking into each of them
            return Object.keys(items).find((key) => items[key].includes(id.toString()));
        },
        [items],
    );

    const handleDragOver = useCallback(
        ({active, over}: DragOverEvent) => {
            if (!over || active.id in items) {
                return;
            }

            const {id: activeId} = active;
            const {id: overId} = over;

            const activeContainer = findContainer(activeId);
            const overContainer = findContainer(overId);

            if (!overContainer || !activeContainer) {
                return;
            }

            if (activeContainer !== overContainer) {
                setItems((items) => {
                    const activeItems = items[activeContainer];
                    const overItems = items[overContainer];
                    const overIndex = overItems.indexOf(overId.toString());
                    const activeIndex = activeItems.indexOf(activeId.toString());

                    const isBelowOverItem =
                        over &&
                        active.rect.current.translated &&
                        active.rect.current.translated.top >
                        over.rect.top + over.rect.height;

                    const modifier = isBelowOverItem ? 1 : 0;

                    const newIndex: number =
                        overIndex >= 0 ? overIndex + modifier : overItems.length + 1;

                    return {
                        ...items,
                        [activeContainer]: items[activeContainer].filter(
                            (item) => item !== active.id,
                        ),
                        [overContainer]: [
                            ...items[overContainer].slice(0, newIndex),
                            items[activeContainer][activeIndex],
                            ...items[overContainer].slice(
                                newIndex,
                                items[overContainer].length,
                            ),
                        ],
                    };
                });
            }
        },
        [items, findContainer],
    );

    return (
        <DndContext
            onDragOver={handleDragOver}
            onDragEnd={(event) => {
                const {active, over} = event;

                if (over != null && active.id !== over.id) {
                    const activeContainerId = findContainer(active.id);

                    if (activeContainerId == null) {
                        return;
                    }

                    setItems((items) => {
                        const containerItems = items[activeContainerId.toString()];

                        const oldIndex = containerItems.indexOf(active.id.toString());
                        const newIndex = containerItems.indexOf(over.id.toString());

                        const nextContainerItems = arrayMove(containerItems, oldIndex, newIndex);

                        return {
                            ...items,
                            [activeContainerId]: nextContainerItems,
                        };
                    });
                }
            }}
        >
            {
                Object.keys(items).map((containerId) => (
                    <ContainerTemplate key={containerId} containerId={containerId} context={props.context}>
                        <SortableContext items={items[containerId]}>
                            {
                                items[containerId].map((id) => (
                                    <SortableItem key={id} id={id} template={ItemTemplate} context={props.context} />
                                ))
                            }
                        </SortableContext>
                    </ContainerTemplate>

                ))
            }

            <Overlay template={ItemTemplate} context={props.context} />

        </DndContext>
    );
}
