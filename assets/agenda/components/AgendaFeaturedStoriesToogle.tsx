import React from 'react';
import Toggle from 'react-toggle';
import {gettext} from 'assets/utils';

interface IProps {
    onChange: any;
    featuredFilter: boolean;
}

function AgendaFeaturedStoriesToggle ({featuredFilter, onChange}: IProps) {
    return (
        <div className="d-flex align-items-center px-2 px-sm-3">
            <div className={'d-flex align-items-center'}>
                <label htmlFor='featured-stories' className="me-2 featured-stories__toggle-label-sm">{gettext('Top/Featured Stories')}</label>
                <label htmlFor='featured-stories' className="me-2 featured-stories__toggle-label-xsm">{gettext('Top Stories')}</label>
                <Toggle
                    id="featured-stories"
                    checked={featuredFilter}
                    className='toggle-background'
                    icons={false}
                    onChange={onChange}/>
            </div>
        </div>

    );
}

export default AgendaFeaturedStoriesToggle;
