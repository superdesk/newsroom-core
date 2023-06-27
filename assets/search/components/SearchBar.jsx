import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {connect} from 'react-redux';

import {gettext} from 'utils';

import {searchQuerySelector} from 'search/selectors';

class SearchBar extends React.Component {
    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this);
        this.onSubmit = this.onSubmit.bind(this);
        this.onClear = this.onClear.bind(this);
        this.onFocus = this.onFocus.bind(this);
        this.state = {query: props.query || ''};
    }

    onChange(event) {
        this.setState({query: event.target.value});
    }

    onSubmit(event) {
        event.preventDefault();
        this.setAndFetch(this.state.query);
    }

    onClear(){
        this.setAndFetch();
        this.setState({query: ''});
    }

    onFocus() {

    }

    setAndFetch(q = '') {
        if (this.props.enableQueryAction) {
            this.props.setQuery(q);
            this.props.fetchItems();
        } else {
            this.props.fetchItems(q);
        }
    }

    componentWillReceiveProps(nextProps) {
        this.setState({query: nextProps.query});
    }

    render() {
        return (
            <React.Fragment>
                <div className="search">
                    <form
                        className={classNames('search__form', {'search__form--active': !!this.state.query,})}
                        role="search"
                        aria-label={gettext('search')}
                        onSubmit={this.onSubmit}>
                        <input
                            type='text'
                            name='q'
                            className='search__input form-control'
                            placeholder={gettext('Search for...')}
                            aria-label={gettext('Search for...')}
                            value={this.state.query || ''}
                            onChange={this.onChange}
                            onFocus={this.onFocus}
                        />
                        <div className='search__form-buttons'>
                            <button
                                className='search__button-clear'
                                aria-label={gettext('Clear search')}
                                onClick={this.onClear}
                                type="reset"
                            >
                                <svg fill="none" height="18" viewBox="0 0 18 18" width="18" xmlns="http://www.w3.org/2000/svg">
                                    <path clipRule="evenodd" d="m9 18c4.9706 0 9-4.0294 9-9 0-4.97056-4.0294-9-9-9-4.97056 0-9 4.02944-9 9 0 4.9706 4.02944 9 9 9zm4.9884-12.58679-3.571 3.57514 3.5826 3.58675-1.4126 1.4143-3.58252-3.5868-3.59233 3.5965-1.41255-1.4142 3.59234-3.59655-3.54174-3.54592 1.41254-1.41422 3.54174 3.54593 3.57092-3.57515z" fill="var(--color-text)" fillRule="evenodd" opacity="1"/>
                                </svg>
                            </button>
                            <button className='search__button-submit' type='submit' aria-label={gettext('Search')}>
                                <i className="icon--search"></i>
                            </button>
                        </div>
                    </form>
                </div>
                <div className="mx-2 d-flex gap-2">
                    {this.props.toggleAdvancedSearchPanel == null ? null : (
                        <button
                            data-test-id="show-advanced-search-panel-btn"
                            className="nh-button nh-button--secondary"
                            onClick={this.props.toggleAdvancedSearchPanel}
                        >
                            {gettext('Advanced Search')}
                        </button>
                    )}
                    <button
                        data-test-id="show-search-tips-panel-btn"
                        className="icon-button icon-button--tertiary icon-button--bordered"
                        aria-label={gettext('Show Search tips')}
                        onClick={this.props.toggleSearchTipsPanel}
                    >
                        <i className="icon--info" />
                    </button>
                </div>
            </React.Fragment>
        );
    }
}

SearchBar.propTypes = {
    query: PropTypes.string,
    setQuery: PropTypes.func,
    fetchItems: PropTypes.func,
    enableQueryAction: PropTypes.bool,
    toggleAdvancedSearchPanel: PropTypes.func,
    toggleSearchTipsPanel: PropTypes.func,
};

const mapStateToProps = (state) => ({
    query: searchQuerySelector(state),
});

SearchBar.defaultProps = {enableQueryAction: true};

export default connect(mapStateToProps, null)(SearchBar);
