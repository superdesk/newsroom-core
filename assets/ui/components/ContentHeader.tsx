import React from 'react';
import PropTypes from 'prop-types';

export default function ContentHeader(props: any) {
    return (
        <section className='content-header'>
            {props.children}
        </section>
    );
}

ContentHeader.propTypes = {
    children: PropTypes.node,
};
