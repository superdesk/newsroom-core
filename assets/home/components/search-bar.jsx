import React from 'react';
import {gettext} from 'utils';
import classNames from 'classnames';

export class SearchBar extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {value: ''};
    }

    render() {
        return (
            <section className="content-header">
                <nav className="content-bar navbar justify-content-start flex-nowrap flex-sm-wrap content-bar--side-padding">
                    <div className="search">
                        <form
                            className={classNames('search__form', {'search__form--active': !!this.state.value,})}
                            action="/wire"
                            role="search"
                            aria-label={gettext('search')}>
                            <input
                                type="text" name="q"
                                className="search__input form-control"
                                placeholder={gettext('Search for...')}
                                aria-label={gettext('Search for...')}
                                onChange={(event) => this.setState({value: event.target.value})}
                            />
                            <div className="search__form-buttons">
                                {this.state.value && (
                                    <button 
                                        type="reset"
                                        className="search__button-clear"
                                        title={gettext('Clear search')}>
                                        <svg fill="none" height="18" viewBox="0 0 18 18" width="18" xmlns="http://www.w3.org/2000/svg">
                                            <path clipRule="evenodd" d="m9 18c4.9706 0 9-4.0294 9-9 0-4.97056-4.0294-9-9-9-4.97056 0-9 4.02944-9 9 0 4.9706 4.02944 9 9 9zm4.9884-12.58679-3.571 3.57514 3.5826 3.58675-1.4126 1.4143-3.58252-3.5868-3.59233 3.5965-1.41255-1.4142 3.59234-3.59655-3.54174-3.54592 1.41254-1.41422 3.54174 3.54593 3.57092-3.57515z" fill="var(--color-text)" fillRule="evenodd" opacity="1"/>
                                        </svg>
                                    </button>
                                )}
                                <button className="search__button-submit" type="submit" title={gettext('Search')}>
                                    <i className="icon--search"></i>
                                </button>
                            </div>
                        </form>
                    </div>
                </nav>
            </section>
        );
    }
}
