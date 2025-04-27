class HistoryProvider:
    """
    히스토리에서 사용하는 유틸리티 함수를 제공하는 클래스
    """
    @staticmethod
    def extract_entity_seq(entity: str, args: tuple, kwargs: dict, param_names: list) -> int | None:
        """
        entity_seq를 다양한 방식으로 추출합니다.:
        1. kwargs에서 직접 추출
        2. param 이름 기준으로 args[idx]에서 추출
        3. DTO 객체 내 속성에서 추출

        Args:
            entity (str): 추출할 entity의 이름
            args (tuple): 함수에 전달된 위치 인수들
            kwargs (dict): 함수에 전달된 키워드 인수들
            param_names (list): 파라미터 이름의 리스트

        Returns:
            int | None: 추출된 entity_seq, 없으면 None
        """
        entity_seq = kwargs.get(f"{entity}_seq")
        if not entity_seq and f"{entity}_seq" in param_names:
            idx = param_names.index(f"{entity}_seq")
            if len(args) > idx:
                entity_seq = args[idx]
        if not entity_seq:
            for arg in args:
                if hasattr(arg, f"{entity}_seq"):
                    entity_seq = getattr(arg, f"{entity}_seq")
                    break
        return entity_seq

    @staticmethod
    def clean_dict(data: dict) -> dict:
        """
        SQLAlchemy ORM 객체의 __dict__에서 내부 상태 필드를 제거합니다.
        (예: _sa_instance_state, children)

        Args:
            data (dict): ORM 객체의 속성을 나타내는 딕셔너리

        Returns:
            dict: 필드를 제거한 깨끗한 딕셔너리
        """
        exclude_fields = (
            "_sa_instance_state",
            "children"
        )
        return {k: v for k, v in data.items() if k not in exclude_fields}