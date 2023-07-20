import React, {useState} from 'react';
import PropTypes from 'prop-types';

export function SidebarFolder({folder, children}) {
    const [open, setOpen] = useState(false);

    return (
        <div className={`collapsible-box collapsible-box--active-within ${open ? 'collapsible-box--open' : 'collapsible-box--closed'}`}>
            <div className="collapsible-box__header" onClick={() => setOpen(!open)} role='button'>
                <h4 className="collapsible-box__header-title">{folder.name}</h4>
                <div className="collapsible-box__header-caret">
                    <i className="icon--arrow-start"></i>
                </div>
            </div>
            <div className="collapsible-box__content">
                <ul className="topic-list">
                    {children}
                </ul>
            </div>
        </div>
    );
}

SidebarFolder.propTypes = {
    folder: PropTypes.object,
    children: PropTypes.node,
};