import React, {useCallback, useEffect} from 'react';
import {Popover, PopoverBody} from 'reactstrap';
import {IFolder} from './TopicFolder';

interface IProps {
    folder: IFolder;
    toggleFolderPopover: (folder: IFolder) => void;
    folderPopover: string;
    actions: Array<any>;
    buttonRef: React.MutableRefObject<any>;
}

export function TopicFolderActions({folder, toggleFolderPopover, folderPopover, actions, buttonRef}: IProps) {
    const elem = document.querySelector('.simple-card__group-header-actions');

    const toggle = useCallback((e) => {
        if (!elem?.contains(e.target)) {
            toggleFolderPopover(folder);
        }
    }, []);

    useEffect(() => {
        document.addEventListener('click', toggle);

        return () => {
            document.removeEventListener('click', toggle);
        };
    });

    return (
        <Popover
            key={'popover-folder-' + folder._id}
            isOpen={folderPopover === folder._id}
            target={buttonRef}
            className="action-popover"
            delay={0}
            fade={false}
        >
            <PopoverBody>
                {
                    actions.map((action: any) => (
                        <button key={action.id}
                            type="button"
                            className="dropdown-item"
                            onClick={(e) => {
                                toggle(e);
                                action.callback();
                            }}
                        >
                            <i className={'icon--' + action.icon} />
                            {action.name}
                        </button>
                    ))
                }
            </PopoverBody>
        </Popover>
    );
}
